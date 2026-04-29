"""
Prezentum — Flask backend
Объединяет генератор презентаций с веб-интерфейсом.
"""

import os
import sys
import uuid
import json
import base64
import threading
import time
from pathlib import Path

from flask import (
    Flask, request, jsonify, send_file,
    render_template, Response
)
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

import generator as gen

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_DIR  = BASE_DIR / "uploads"
OUTPUT_DIR  = BASE_DIR / "outputs"
IMAGES_DIR  = BASE_DIR / "outputs" / "images"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

JOBS: dict = {}
JOBS_LOCK = threading.Lock()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    try:
        if suffix == ".pdf":
            import pdfplumber
            text_parts = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            return "\n".join(text_parts)
        elif suffix == ".docx":
            from docx import Document
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"[Не удалось извлечь текст: {e}]"
    return ""


def run_generation(job_id: str, params: dict):
    """Запускает генерацию в отдельном потоке."""

    def log(msg: str):
        with JOBS_LOCK:
            JOBS[job_id]["log"].append(msg)

    def set_progress(pct: int):
        with JOBS_LOCK:
            JOBS[job_id]["progress"] = pct

    def store_image(slide_idx: int, img_bytes: bytes):
        """Сохраняет картинку и кладёт base64 в JOBS."""
        try:
            fname = IMAGES_DIR / f"{job_id}_slide{slide_idx}.png"
            fname.write_bytes(img_bytes)
            b64 = base64.b64encode(img_bytes).decode()
            with JOBS_LOCK:
                JOBS[job_id]["images"][slide_idx] = f"data:image/png;base64,{b64}"
        except Exception as e:
            log(f"  ⚠ Не удалось сохранить картинку слайда {slide_idx}: {e}")

    try:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "running"

        source_text = params["source_text"]
        n_slides    = int(params.get("n_slides", 7))
        img_choice  = params.get("img_choice", "none")
        gen_type    = params.get("gen_type", "тезисная")
        author      = params.get("author", "").strip()
        out_name    = f"prezentum_{job_id[:8]}"

        if gen_type == "тезисная":
            source_text = (
                "РЕЖИМ ТЕЗИСНОЙ ПРЕЗЕНТАЦИИ: Используй краткие тезисы, минимум текста на слайде, "
                "только ключевые факты и утверждения. Никаких длинных абзацев.\n\n"
                + source_text
            )
        else:
            source_text = (
                "РЕЖИМ ПОДРОБНОЙ ТЕКСТОВОЙ ПРЕЗЕНТАЦИИ: Давай развёрнутые описания, "
                "подробные объяснения, академический стиль, полные предложения.\n\n"
                + source_text
            )

        log("🔍 Анализ темы и определение стиля...")
        set_progress(5)

        try:
            style_key, tone_key = gen.detect_style_and_tone(source_text)
        except Exception as e:
            log(f"⚠ Стиль/тон по умолчанию ({e})")
            style_key, tone_key = "корпоративный", "нейтральный"

        log(f"✦ Стиль: {style_key}  |  Тон: {tone_key}")
        set_progress(10)

        force_highlight = gen._wants_highlight(source_text)
        if force_highlight:
            log("✦ Включён режим highlight_block")

        log(f"🤖 Генерация структуры ({n_slides} слайдов)...")
        set_progress(15)

        slides_data = gen.generate_structure(
            source_text, n_slides, tone_key,
            force_highlight=force_highlight
        )

        if author and slides_data:
            first = slides_data[0]
            if first.get("_type") == "title":
                existing_sub = first.get("subtitle", "")
                first["subtitle"] = f"{existing_sub}  |  {author}".strip(" |") if existing_sub else author

        log(f"✅ Структура готова — {len(slides_data)} слайдов")
        set_progress(30)

        style = gen.STYLES[style_key]

        gen_images = img_choice != "none"
        use_yandex = img_choice == "yandex"

        pptx_path = str(OUTPUT_DIR / f"{out_name}.pptx")
        pdf_path  = str(OUTPUT_DIR / f"{out_name}.pdf")

        # ── Перехватываем генерацию изображений ────────────────────────────
        # Патчим generate_image чтобы перехватывать байты и сохранять их
        original_generate_image = gen.generate_image
        captured_slide_idx = [0]  # счётчик слайдов с картинками

        def patched_generate_image(prompt, style_suffix, use_yandex=False):
            img_bytes = original_generate_image(prompt, style_suffix, use_yandex)
            if img_bytes:
                store_image(captured_slide_idx[0], img_bytes)
            captured_slide_idx[0] += 1
            return img_bytes

        gen.generate_image = patched_generate_image

        import builtins
        original_print = builtins.print

        def patched_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            log(msg)

        builtins.print = patched_print

        try:
            # Прогресс картинок: каждый слайд ~= (80-30)/n_slides процентов
            per_slide_pct = (80 - 30) / max(n_slides, 1)

            if gen_images:
                log("🎨 Генерация изображений и сборка PPTX...")
            else:
                log("🎨 Сборка PPTX...")

            # Патчим build_pptx чтобы обновлять прогресс по слайдам
            original_build_pptx = gen.build_pptx

            def patched_build_pptx(slides_data_in, style_in, output_path,
                                   generate_images=True, use_yandex=False):
                # Вызываем оригинал (он внутри вызывает generate_image для каждого слайда)
                original_build_pptx(slides_data_in, style_in, output_path,
                                    generate_images=generate_images, use_yandex=use_yandex)

            gen.build_pptx = patched_build_pptx

            gen.build_pptx(
                slides_data, style, pptx_path,
                generate_images=gen_images,
                use_yandex=use_yandex
            )
            set_progress(80)

            log("📄 Конвертация в PDF...")
            gen.pptx_to_pdf(None, pdf_path, slides_data, style)
            set_progress(95)

        finally:
            builtins.print = original_print
            gen.generate_image = original_generate_image

        log("✅ Готово!")
        set_progress(100)

        with JOBS_LOCK:
            JOBS[job_id]["status"]      = "done"
            JOBS[job_id]["pptx_file"]   = out_name + ".pptx"
            JOBS[job_id]["pdf_file"]    = out_name + ".pdf"
            JOBS[job_id]["slides_data"] = slides_data
            JOBS[job_id]["style"]       = style_key

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["log"].append(f"❌ Ошибка: {e}")
            JOBS[job_id]["log"].append(err)


# ── Маршруты ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    prompt     = request.form.get("prompt", "").strip()
    n_slides   = int(request.form.get("n_slides", 7))
    img_choice = request.form.get("img_choice", "none")
    gen_type   = request.form.get("gen_type", "тезисная")
    author     = request.form.get("author", "")

    file_texts = []
    for key in ("file1", "file2"):
        f = request.files.get(key)
        if f and f.filename and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            save_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{fname}"
            f.save(save_path)
            extracted = extract_text_from_file(save_path)
            if extracted:
                file_texts.append(f"=== Содержимое файла {fname} ===\n{extracted}")

    source_text = prompt
    if file_texts:
        source_text = "\n\n".join(file_texts)
        if prompt:
            source_text = prompt + "\n\n" + source_text

    if not source_text:
        return jsonify({"error": "Введите тему или прикрепите файл"}), 400

    job_id = str(uuid.uuid4())
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status":      "queued",
            "progress":    0,
            "log":         [],
            "images":      {},   # slide_idx → "data:image/png;base64,..."
            "pptx_file":   None,
            "pdf_file":    None,
            "slides_data": None,
            "style":       None,
        }

    params = {
        "source_text": source_text,
        "n_slides":    n_slides,
        "img_choice":  img_choice,
        "gen_type":    gen_type,
        "author":      author,
    }

    t = threading.Thread(target=run_generation, args=(job_id, params), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def api_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "status":      job["status"],
        "progress":    job["progress"],
        "log":         job["log"][-30:],
        "images":      job.get("images", {}),
        "pptx_file":   job.get("pptx_file"),
        "pdf_file":    job.get("pdf_file"),
        "slides_data": job.get("slides_data"),
        "style":       job.get("style"),
    })


@app.route("/api/download/<filename>")
def api_download(filename: str):
    safe = secure_filename(filename)
    path = OUTPUT_DIR / safe
    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True, download_name=safe)


@app.route("/api/styles")
def api_styles():
    return jsonify({
        "styles": list(gen.STYLES.keys()),
        "tones":  list(gen.TONES.keys()),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
