/*=====================================================================
   UI‑логика проекта (отдельный файл)
   • Drag‑&‑Drop + обычный File‑input
   • Формируем FormData и отправляем POST‑запрос к /api/generate
   • Отрисовываем полученные слайды
   • Управление лоадером, блокировка кнопки, экспорт PPTX
=====================================================================*/

const state = {
    file: null,
    isGenerating: false,
};

/* ---------- Элементы DOM ---------- */
const dropZone      = document.getElementById('dropZone');
const fileInput     = document.getElementById('fileInput');
const fileNameDisp  = document.getElementById('fileName');
const generateBtn   = document.getElementById('generateBtn');
const previewArea   = document.getElementById('previewArea');
const loader        = document.getElementById('loader');
const loadingText   = document.getElementById('loadingText');

/* ---------- Drag & Drop ---------- */
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
    state.file = file;
    fileNameDisp.textContent = `📄 ${file.name}`;
    fileNameDisp.style.display = 'block';
    dropZone.style.borderColor = 'var(--accent-color)';
}

/* ---------- Кнопка «Сгенерировать» ---------- */
generateBtn.addEventListener('click', async () => {
    const prompt      = document.getElementById('promptInput').value.trim();
    const slideCount  = document.getElementById('slideCount').value;
    const style       = document.getElementById('styleSelect').value;
    const tone        = document.getElementById('toneSelect').value;
    const imgService  = document.getElementById('imageServiceSelect')
                            ? document.getElementById('imageServiceSelect').value
                            : 'sd';

    // ---- простая валидация ----
    if (!prompt && !state.file) {
        alert('Введите тему или загрузите документ.');
        return;
    }

    startGeneration();

    // ---- Формируем multipart/form-data ----
    const formData = new FormData();
    if (prompt)      formData.append('prompt', prompt);
    if (state.file)  formData.append('file', state.file);
    formData.append('slides', slideCount);
    formData.append('style', style);
    formData.append('tone', tone);
    formData.append('image_service', imgService);

    try {
        // ---- POST‑запрос к FastAPI ----
        const response = await fetch('/api/generate', {
            method: 'POST',
            body:   formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        renderSlides(data.slides);
    } catch (e) {
        console.error(e);
        alert(`Ошибка генерации: ${e.message}`);
    } finally {
        stopGeneration();
    }
});

/* ---------- UI‑утилиты ---------- */
function startGeneration() {
    state.isGenerating = true;
    generateBtn.disabled = true;
    loader.style.display = 'flex';
}
function stopGeneration() {
    state.isGenerating = false;
    generateBtn.disabled = false;
    loader.style.display = 'none';
}

/* ---------- Отрисовка слайдов ---------- */
function renderSlides(slides) {
    console.log('📊 Получено слайдов:', slides?.length || 0);
    console.log('📄 Данные слайдов:', slides);

    if (!slides || !Array.isArray(slides) || slides.length === 0) {
        alert('⚠️ Слайды не получены или пустые!');
        return;
    }

    previewArea.innerHTML = '';

    slides.forEach((slide, idx) => {
        const title = slide.title || slide.title_text || `Слайд ${idx + 1}`;
        const bullets = slide.bullets || slide.points || [];
        const imageUrl = slide.image_url || slide.image || null;

        console.log(`🔹 Слайд ${idx + 1}:`, { title, bulletsCount: bullets.length, hasImage: !!imageUrl });

        const el = document.createElement('div');
        el.className = 'slide-container';

        if (document.getElementById('styleSelect').value === 'dark') {
            el.style.background = '#1f2937';
            el.style.color = '#fff';
        }

        const bulletsHtml = bullets.length > 0
            ? bullets.map(b => `<li>${b}</li>`).join('')
            : '<li>Нет содержимого</li>';

        const imgHtml = imageUrl
            ? `<img src="${imageUrl}" alt="AI Image" onerror="this.src='https://placehold.co/600x400?text=Image+Error'">`
            : '<span>AI Generated Image</span>';

        el.innerHTML = `
            <div class="slide-header">${title}</div>
            <div class="slide-content">
                <ul class="slide-text">${bulletsHtml}</ul>
                <div class="slide-image-placeholder">${imgHtml}</div>
            </div>
            <div class="slide-number">${idx + 1} / ${slides.length}</div>
        `;
        previewArea.appendChild(el);
    });

    console.log('✅ Рендеринг завершён');
}

/* ---------- Экспорт PPTX (реальный) ---------- */
async function exportPPTX() {
    // Собираем слайды из отображённых элементов
    const slideElements = document.querySelectorAll('.slide-container');
    
    if (slideElements.length === 0) {
        alert('Сначала создайте презентацию!');
        return;
    }

    const slides = [];
    slideElements.forEach(el => {
        const title = el.querySelector('.slide-header')?.innerText || 'Без названия';
        const bullets = Array.from(el.querySelectorAll('.slide-text li'))
            .map(li => li.innerText.replace('Нет содержимого', '').trim())
            .filter(b => b.length > 0);
        const img = el.querySelector('.slide-image-placeholder img');
        const imageUrl = img && img.src.includes('placehold.co') ? null : (img?.src || null);
        
        slides.push({ title, bullets, image_url: imageUrl });
    });

    const presentationData = {
        title: document.getElementById('promptInput').value.trim() || 'Презентация',
        slides: slides
    };

    const style = document.getElementById('styleSelect').value;

    alert('Генерация .pptx файла...');
    
    try {
        const formData = new FormData();
        formData.append('presentation_data', JSON.stringify(presentationData));
        formData.append('style', style);

        const response = await fetch('/api/export/pptx', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка генерации PPTX');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `presentation_${new Date().getTime()}.pptx`;
        a.click();
        URL.revokeObjectURL(url);

        alert('Файл PPTX скачан!');
    } catch (e) {
        console.error(e);
        alert(`Ошибка: ${e.message}`);
    }
}

/* ---------- Mock‑данные (fallback) ---------- */
function generateMockSlides(prompt, count) {
    const slides = [];
    for (let i = 0; i < count; i++) {
        slides.push({
            title: i === 0 ? (prompt || 'Введение') : `Слайд ${i + 1}: Детализация`,
            bullets: [
                'Ключевой тезис, сгенерированный LLM на основе вашего запроса.',
                'Второй важный пункт, полученный из загруженного документа.',
                'Аналитика и выводы по текущему этапу.'
            ],
            image_url: i % 2 === 0
                ? 'https://placehold.co/600x400/7d3aff/white?text=AI+Image'
                : null
        });
    }
    return slides;
}
