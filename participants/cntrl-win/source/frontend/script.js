// ============================================
// Конфигурация
// ============================================
const API_URL = 'http://127.0.0.1:8000';
const LS_THEME_KEY = 'presgen-theme';
const LS_LANG_KEY = 'presgen-lang';

const translations = {
    ru: {
        fileLoaded: 'Файл загружен',
        onlyPdfDocx: 'Только PDF и DOCX',
        maxSize: 'Максимум 16 МБ',
        enterTopic: 'Введите тему или загрузите файл',
        ready: 'Презентация готова!',
        downloaded: 'Презентация скачана',
        error: 'Ошибка',
        preparing: 'Подготовка...',
        sending: 'Отправка...',
        generatingContent: 'Генерация контента...',
        saving: 'Сохранение...',
        done: 'Готово',
        formReset: 'Форма сброшена',
        createFirst: 'Сначала создайте презентацию',
    },
    en: {
        fileLoaded: 'File loaded',
        onlyPdfDocx: 'Only PDF and DOCX',
        maxSize: 'Max 16 MB',
        enterTopic: 'Enter topic or upload file',
        ready: 'Presentation ready!',
        downloaded: 'Presentation downloaded',
        error: 'Error',
        preparing: 'Preparing...',
        sending: 'Sending...',
        generatingContent: 'Generating content...',
        saving: 'Saving...',
        done: 'Done',
        formReset: 'Form reset',
        createFirst: 'Create presentation first',
    }
};

let currentLang = localStorage.getItem(LS_LANG_KEY) || 'ru';
let currentTheme = localStorage.getItem(LS_THEME_KEY) || 'light';
let selectedFile = null;
let pptBlob = null;
let slides = [];
let currentSlide = 0;

document.addEventListener('DOMContentLoaded', () => {
    applyTheme(currentTheme);
    applyLanguage(currentLang);
    bindEvents();
    console.log('🚀 Ready');
});

function bindEvents() {
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('langToggle').addEventListener('click', toggleLanguage);

    document.getElementById('startBtn').addEventListener('click', () => {
        document.getElementById('hero').style.display = 'none';
        document.getElementById('generatorLayout').style.display = 'grid';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    document.getElementById('prompt').addEventListener('input', () => {
        const textarea = document.getElementById('prompt');
        document.getElementById('charCount').textContent = textarea.value.length;
        if (textarea.value.trim()) {
            textarea.style.borderColor = 'var(--border)';
            textarea.style.boxShadow = 'none';
        }
    });

    const ua = document.getElementById('uploadArea');
    const fi = document.getElementById('fileInput');
    ua.addEventListener('click', () => fi.click());
    ua.addEventListener('dragover', e => { e.preventDefault(); ua.style.borderColor = 'var(--primary)'; });
    ua.addEventListener('dragleave', () => { ua.style.borderColor = 'var(--border)'; });
    ua.addEventListener('drop', e => {
        e.preventDefault();
        ua.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });
    fi.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });
    document.getElementById('removeFile').addEventListener('click', e => { e.stopPropagation(); removeFile(); });

    document.getElementById('nextStep').addEventListener('click', () => {
        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt && !selectedFile) {
            toast(t('enterTopic'), 'error');
            const textarea = document.getElementById('prompt');
            textarea.style.borderColor = 'var(--error)';
            textarea.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
            textarea.style.animation = 'shake 0.5s ease';
            setTimeout(() => {
                textarea.style.borderColor = 'var(--border)';
                textarea.style.boxShadow = 'none';
                textarea.style.animation = '';
            }, 2000);
            return;
        }
        switchStep(2);
    });

    document.getElementById('prevStep').addEventListener('click', () => switchStep(1));
    document.getElementById('decSlides').addEventListener('click', () => adjustSlides(-1));
    document.getElementById('incSlides').addEventListener('click', () => adjustSlides(1));

    document.getElementById('generateForm').addEventListener('submit', e => { e.preventDefault(); generate(); });
    document.getElementById('generateBtn').addEventListener('click', generate);
    document.getElementById('prevSlide').addEventListener('click', () => navSlide(-1));
    document.getElementById('nextSlide').addEventListener('click', () => navSlide(1));
    document.getElementById('downloadBtn').addEventListener('click', download);
    document.getElementById('resetBtn').addEventListener('click', reset);

    // Установка начального placeholder для всех полей с data-*-placeholder
    document.querySelectorAll('textarea[data-ru-placeholder][data-en-placeholder], input[data-ru-placeholder][data-en-placeholder]').forEach(el => {
        const ph = el.getAttribute(`data-${currentLang}-placeholder`);
        if (ph) {
            el.placeholder = ph;
        }
    });
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem(LS_THEME_KEY, currentTheme);
    applyTheme(currentTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelector('.theme-icon-sun').style.display = theme === 'light' ? 'inline' : 'none';
    document.querySelector('.theme-icon-moon').style.display = theme === 'dark' ? 'inline' : 'none';
}

function toggleLanguage() {
    currentLang = currentLang === 'ru' ? 'en' : 'ru';
    localStorage.setItem(LS_LANG_KEY, currentLang);
    applyLanguage(currentLang);
}

// ============================================
// Функция смены языка на сайте
// ============================================
function applyLanguage(lang) {
    document.documentElement.lang = lang;
    document.getElementById('langText').textContent = lang === 'ru' ? 'RU' : 'EN';

    // Обработка всех элементов с data-ru/data-en
    document.querySelectorAll('[data-ru][data-en]').forEach(el => {
        const text = el.getAttribute(`data-${lang}`);
        if (text === null) return;

        if (el.tagName === 'TEXTAREA') {
            // Обновляем placeholder
            const ph = el.getAttribute(`data-${lang}-placeholder`);
            if (ph !== null) {
                el.placeholder = ph;
            }
        } else if (el.tagName === 'OPTION') {
            el.textContent = text;
        } else if (!el.querySelector('[data-ru]')) {
            el.textContent = text;
        }
    });

    // Дополнительно: обновляем placeholder для всех textarea с data-*-placeholder
    document.querySelectorAll('textarea[data-ru-placeholder][data-en-placeholder]').forEach(el => {
        const ph = el.getAttribute(`data-${lang}-placeholder`);
        if (ph !== null) {
            el.placeholder = ph;
        }
    });

    // Обновляем title атрибуты
    document.querySelectorAll('[data-ru-title][data-en-title]').forEach(el => {
        const t = el.getAttribute(`data-${lang}-title`);
        if (t !== null) el.title = t;
    });

    // Обновляем hero элементы
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroQuote = document.querySelector('.hero-quote');
    if (heroSubtitle) {
        heroSubtitle.textContent = heroSubtitle.getAttribute(`data-${lang}`);
    }
    if (heroQuote) {
        heroQuote.textContent = heroQuote.getAttribute(`data-${lang}`);
    }
}

function t(key) { return translations[currentLang]?.[key] || key; }

function handleFile(file) {
    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) return toast(t('onlyPdfDocx'), 'error');
    if (file.size > 16*1024*1024) return toast(t('maxSize'), 'error');
    selectedFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatSize(file.size);
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('uploadFile').style.display = 'flex';
    toast(t('fileLoaded'), 'success');
}

function removeFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('uploadFile').style.display = 'none';
}

function adjustSlides(d) {
    const i = document.getElementById('slidesCount');
    i.value = Math.max(1, Math.min(20, parseInt(i.value)+d));
}

function switchStep(s) {
    document.querySelectorAll('.form-step').forEach(e => e.classList.remove('active'));
    const formStep = document.getElementById(`formStep${s}`);
    if (formStep) formStep.classList.add('active');

    document.querySelectorAll('.step').forEach(st => {
        const n = parseInt(st.dataset.step);
        st.classList.remove('active', 'completed');
        if (n < s) st.classList.add('completed');
        else if (n === s) st.classList.add('active');
    });
}

async function generate() {
    const prompt = document.getElementById('prompt').value.trim();
    if (!prompt && !selectedFile) return toast(t('enterTopic'), 'error');

    setLoading(true);

    const fd = new FormData();
    fd.append('prompt', prompt);
    fd.append('slides_count', document.getElementById('slidesCount').value);
    fd.append('style', document.getElementById('style').value);
    fd.append('tone', document.getElementById('tone').value);
    if (selectedFile) fd.append('file', selectedFile);

    try {
        updateProgress(10, t('preparing'));
        updateProgress(30, t('sending'));

        const res = await fetch(`${API_URL}/generate-presentation`, {
            method: 'POST',
            body: fd
        });

        updateProgress(60, t('generatingContent'));

        if (!res.ok) {
            let e = `Error ${res.status}`;
            try { const j = await res.json(); e = j.detail || e; } catch(_) {}
            throw new Error(e);
        }

        updateProgress(80, t('saving'));
        pptBlob = await res.blob();
        if (!pptBlob.size) throw new Error('Empty response');

        updateProgress(100, t('done'));

        slides = await parsePptx(pptBlob);
        currentSlide = 0;

        setTimeout(() => {
            setLoading(false);
            showSlides();

            document.querySelectorAll('.step').forEach(st => {
                st.classList.remove('active');
                st.classList.add('completed');
            });

            toast(t('ready'), 'success');
            setTimeout(download, 500);
        }, 500);

    } catch(e) {
        setLoading(false);
        switchStep(1);
        toast(`${t('error')}: ${e.message}`, 'error');
    }
}

async function parsePptx(blob) {
    try {
        const arrayBuffer = await blob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        const unzipped = fflate.unzipSync(uint8Array);
        const slideFiles = [];

        for (const [filename, data] of Object.entries(unzipped)) {
            const match = filename.match(/^ppt\/slides\/slide(\d+)\.xml$/);
            if (match) {
                const decoder = new TextDecoder('utf-8');
                const xmlText = decoder.decode(data);
                slideFiles.push({
                    num: parseInt(match[1]),
                    xml: xmlText
                });
            }
        }

        slideFiles.sort((a, b) => a.num - b.num);
        const slides = [];

        for (const sf of slideFiles) {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(sf.xml, 'text/xml');
            const textElements = xmlDoc.getElementsByTagName('a:t');
            const texts = [];

            for (let i = 0; i < textElements.length; i++) {
                const text = textElements[i].textContent;
                if (text && text.trim()) texts.push(text.trim());
            }

            const title = texts[0] || `Слайд ${sf.num}`;
            const items = texts.slice(1);

            slides.push({
                number: sf.num,
                title: title,
                items: items.length > 0 ? items : ['Содержимое слайда'],
                isTitle: sf.num === 1,
                isFinal: sf.num === slideFiles.length
            });
        }

        if (slides.length > 0) return slides;
    } catch (e) {
        console.log('⚠️ Ошибка парсинга PPTX:', e.message);
    }
    return generateDemoSlides();
}

function generateDemoSlides() {
    const prompt = document.getElementById('prompt').value.trim();
    const count = parseInt(document.getElementById('slidesCount').value) || 5;
    const slides = [];

    slides.push({
        number: 1,
        title: prompt || 'Презентация',
        items: [`Тема: ${prompt || 'Не указана'}`, `Дата: ${new Date().toLocaleDateString('ru-RU')}`, 'AI Presentation Generator'],
        isTitle: true
    });

    const templates = [
        { title: 'Введение', items: ['Обзор темы', 'Ключевые понятия', 'Цели презентации'] },
        { title: 'Основная часть', items: ['Пункт 1', 'Пункт 2', 'Пункт 3'] },
        { title: 'Анализ', items: ['Текущая ситуация', 'Данные', 'Тенденции'] },
        { title: 'Решения', items: ['Подходы', 'Преимущества', 'План'] },
        { title: 'Примеры', items: ['Кейс 1', 'Кейс 2', 'Результаты'] },
    ];

    for (let i = 1; i < count - 1; i++) {
        const t = templates[Math.min(i - 1, templates.length - 1)];
        slides.push({ number: i + 1, title: t.title, items: t.items });
    }

    if (count > 1) {
        slides.push({
            number: count,
            title: 'Заключение',
            items: ['Основные выводы', 'Рекомендации', 'Спасибо за внимание!'],
            isFinal: true
        });
    }

    return slides;
}

function showSlides() {
    document.getElementById('stateEmpty').style.display = 'none';
    document.getElementById('stateLoading').style.display = 'none';
    document.getElementById('stateSlides').style.display = 'block';
    document.getElementById('previewToolbar').style.display = 'flex';
    renderSlide();
    renderDots();
}

function renderSlide() {
    if (!slides.length) return;
    const s = slides[currentSlide];
    let html = '';

    if (s.isTitle) {
        html = `<div style="text-align:center;padding:30px 20px;">
            <h3 style="font-size:28px;margin-bottom:30px;color:var(--primary);">${esc(s.title)}</h3>
            ${s.items.map(i => `<div style="margin-bottom:10px;font-size:16px;color:var(--text-secondary);">${esc(i)}</div>`).join('')}
        </div>`;
    } else if (s.isFinal) {
        html = `<div style="text-align:center;padding:30px 20px;">
            <h3 style="font-size:28px;margin-bottom:30px;color:var(--success);">${esc(s.title)}</h3>
            ${s.items.map(i => `<div style="margin-bottom:12px;font-size:18px;color:var(--text-secondary);">${esc(i)}</div>`).join('')}
        </div>`;
    } else {
        html = `<h3 style="font-size:24px;font-weight:700;margin-bottom:20px;padding-bottom:12px;border-bottom:3px solid var(--primary);">${esc(s.title)}</h3>
        <ul style="list-style:none;padding:0;">
            ${s.items.map(i => `<li style="padding:10px 0 10px 25px;position:relative;font-size:16px;color:var(--text-secondary);">${esc(i)}</li>`).join('')}
        </ul>`;
    }

    document.getElementById('slideView').innerHTML = html;
    document.getElementById('slideCounter').textContent = `${currentSlide + 1} / ${slides.length}`;
    document.getElementById('prevSlide').disabled = currentSlide === 0;
    document.getElementById('nextSlide').disabled = currentSlide === slides.length - 1;
}

function renderDots() {
    document.getElementById('slideDots').innerHTML = slides.map((_, i) =>
        `<div class="dot ${i === currentSlide ? 'active' : ''}" onclick="navTo(${i})"></div>`
    ).join('');
}

function navSlide(d) { currentSlide = Math.max(0, Math.min(slides.length-1, currentSlide+d)); renderSlide(); renderDots(); }
function navTo(i) { currentSlide = i; renderSlide(); renderDots(); }

function download() {
    if (!pptBlob) return toast(t('createFirst'), 'error');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(pptBlob);
    a.download = `presentation_${Date.now()}.pptx`;
    a.click();
    URL.revokeObjectURL(a.href);
    toast(t('downloaded'), 'success');
}

function reset() {
    pptBlob = null; slides = []; currentSlide = 0;
    document.getElementById('stateEmpty').style.display = 'block';
    document.getElementById('stateSlides').style.display = 'none';
    document.getElementById('previewToolbar').style.display = 'none';
    document.getElementById('slideView').innerHTML = '';
    document.getElementById('slideDots').innerHTML = '';

    document.querySelectorAll('.step').forEach(st => st.classList.remove('active', 'completed'));
    const firstStep = document.querySelector('.step[data-step="1"]');
    if (firstStep) firstStep.classList.add('active');

    document.querySelectorAll('.form-step').forEach(e => e.classList.remove('active'));
    const formStep1 = document.getElementById('formStep1');
    if (formStep1) formStep1.classList.add('active');

    toast(t('formReset'), 'info');
}

function setLoading(v) {
    document.getElementById('stateEmpty').style.display = v ? 'none' : 'block';
    document.getElementById('stateLoading').style.display = v ? 'block' : 'none';
    document.getElementById('stateSlides').style.display = 'none';
    const btn = document.getElementById('generateBtn');
    btn.querySelector('.btn-text').style.display = v ? 'none' : 'inline';
    btn.querySelector('.btn-loader').style.display = v ? 'flex' : 'none';
    btn.disabled = v;
}

function updateProgress(p, txt) {
    document.getElementById('progressFill').style.width = p + '%';
    document.getElementById('loadingText').textContent = txt;
}

function toast(msg, type = 'info') {
    const c = document.getElementById('toasts');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 4000);
}

function formatSize(b) { return b < 1024 ? b + ' B' : b < 1024*1024 ? (b/1024).toFixed(1)+' KB' : (b/1024/1024).toFixed(1)+' MB'; }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
