// ============================================
// CONFIGURATION
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
        slide1: 'Титульный слайд',
        slide2: 'Введение',
        slide3: 'Основная часть',
        slide4: 'Анализ',
        slide5: 'Решения',
        slide6: 'Заключение',
        slide7: 'Итоги',
        item1: 'Основной пункт',
        item2: 'Дополнительная информация',
        item3: 'Ключевые моменты',
        heroSubtitle: 'Эстетика автоматизации',
        heroQuote: '«Хватит тратить часы на дизайн — выбери AI и сделай красиво за несколько секунд.»',
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
        slide1: 'Title Slide',
        slide2: 'Introduction',
        slide3: 'Main Content',
        slide4: 'Analysis',
        slide5: 'Solutions',
        slide6: 'Conclusion',
        slide7: 'Summary',
        item1: 'Main point',
        item2: 'Additional information',
        item3: 'Key highlights',
        heroSubtitle: 'Aesthetics of Automation',
        heroQuote: '«Stop wasting hours on design — choose AI and make it beautiful in seconds.»',
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

    document.getElementById('prompt').addEventListener('input', () => {
        document.getElementById('charCount').textContent = document.getElementById('prompt').value.length;
    });

    document.getElementById('nextStep').addEventListener('click', () => switchStep(2));
    document.getElementById('prevStep').addEventListener('click', () => switchStep(1));
    document.getElementById('decSlides').addEventListener('click', () => adjustSlides(-1));
    document.getElementById('incSlides').addEventListener('click', () => adjustSlides(1));

    document.getElementById('generateForm').addEventListener('submit', e => { e.preventDefault(); generate(); });
    document.getElementById('generateBtn').addEventListener('click', generate);
    document.getElementById('prevSlide').addEventListener('click', () => navSlide(-1));
    document.getElementById('nextSlide').addEventListener('click', () => navSlide(1));
    document.getElementById('downloadBtn').addEventListener('click', download);
    document.getElementById('resetBtn').addEventListener('click', reset);
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
    // Инвертируем язык
    currentLang = currentLang === 'ru' ? 'en' : 'ru';
    localStorage.setItem(LS_LANG_KEY, currentLang);
    applyLanguage(currentLang);
}

function applyLanguage(lang) {
    document.documentElement.lang = lang;

    // Кнопка языка: RU когда русский, EN когда английский
    document.getElementById('langText').textContent = lang === 'ru' ? 'RU' : 'EN';

    // Обновляем все элементы с data-ru/data-en
    document.querySelectorAll('[data-ru][data-en]').forEach(el => {
        const text = el.getAttribute(`data-${lang}`);
        if (text === null) return;

        if (el.tagName === 'TEXTAREA') {
            const ph = el.getAttribute(`data-${lang}-placeholder`);
            if (ph !== null) el.placeholder = ph;
        } else if (el.tagName === 'OPTION') {
            el.textContent = text;
        } else if (!el.querySelector('[data-ru]')) {
            // Только если нет вложенных data-ru элементов
            el.textContent = text;
        }
    });

    // Обновляем title атрибуты
    document.querySelectorAll('[data-ru-title][data-en-title]').forEach(el => {
        const t = el.getAttribute(`data-${lang}-title`);
        if (t !== null) el.title = t;
    });

    // Обновляем hero подзаголовок и цитату (они используют data-ru/data-en)
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroQuote = document.querySelector('.hero-quote');

    if (heroSubtitle) {
        heroSubtitle.textContent = heroSubtitle.getAttribute(`data-${lang}`);
    }
    if (heroQuote) {
        heroQuote.textContent = heroQuote.getAttribute(`data-${lang}`);
    }

    // Обновляем превью если есть слайды
    if (slides.length > 0) {
        slides = generatePreview();
        renderSlide();
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

function adjustSlides(d) { const i = document.getElementById('slidesCount'); i.value = Math.max(1, Math.min(20, parseInt(i.value)+d)); }

function switchStep(s) {
    document.querySelectorAll('.form-step').forEach(e => e.classList.remove('active'));
    document.getElementById(`formStep${s}`).classList.add('active');
    document.querySelectorAll('.step').forEach(st => {
        const n = parseInt(st.dataset.step);
        st.classList.remove('active', 'completed');
        if (n < s) st.classList.add('completed');
        if (n === s) st.classList.add('active');
    });
}

async function generate() {
    const prompt = document.getElementById('prompt').value.trim();
    if (!prompt && !selectedFile) return toast(t('enterTopic'), 'error');
    setLoading(true);
    switchStep(2);

    const fd = new FormData();
    fd.append('prompt', prompt);
    fd.append('slides_count', document.getElementById('slidesCount').value);
    fd.append('style', document.getElementById('style').value);
    fd.append('tone', document.getElementById('tone').value);
    if (selectedFile) fd.append('file', selectedFile);

    try {
        updateProgress(10, t('preparing'));
        updateProgress(30, t('sending'));
        const res = await fetch(`${API_URL}/generate-presentation`, { method: 'POST', body: fd });
        updateProgress(60, t('generatingContent'));
        if (!res.ok) { let e = `Error ${res.status}`; try { const j = await res.json(); e = j.detail || e; } catch(_){} throw new Error(e); }
        updateProgress(80, t('saving'));
        pptBlob = await res.blob();
        if (!pptBlob.size) throw new Error('Empty');
        updateProgress(100, t('done'));
        slides = generatePreview();
        currentSlide = 0;
        setTimeout(() => { setLoading(false); showSlides(); switchStep(3); toast(t('ready'),'success'); setTimeout(download,500); }, 500);
    } catch(e) { setLoading(false); switchStep(1); toast(`${t('error')}: ${e.message}`,'error'); }
}

function generatePreview() {
    const c = parseInt(document.getElementById('slidesCount').value) || 5;
    const g = [
        { title: t('slide1'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide2'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide3'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide4'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide5'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide6'), items: [t('item1'),t('item2'),t('item3')] },
        { title: t('slide7'), items: [t('item1'),t('item2'),t('item3')] },
    ];
    return Array.from({length:c}, (_,i)=>({...g[Math.min(i,g.length-1)], number:i+1}));
}

function showSlides() {
    document.getElementById('stateEmpty').style.display='none';
    document.getElementById('stateLoading').style.display='none';
    document.getElementById('stateSlides').style.display='block';
    document.getElementById('previewToolbar').style.display='flex';
    renderSlide(); renderDots();
}

function renderSlide() {
    if(!slides.length) return;
    const s = slides[currentSlide];
    document.getElementById('slideView').innerHTML = `<h3>${esc(s.title)}</h3><ul>${s.items.map(i=>`<li>${esc(i)}</li>`).join('')}</ul>`;
    document.getElementById('slideCounter').textContent = `${currentSlide+1} / ${slides.length}`;
    document.getElementById('prevSlide').disabled = currentSlide===0;
    document.getElementById('nextSlide').disabled = currentSlide===slides.length-1;
}

function renderDots() {
    document.getElementById('slideDots').innerHTML = slides.map((_,i)=>`<div class="dot ${i===currentSlide?'active':''}" onclick="navTo(${i})"></div>`).join('');
}

function navSlide(d) { currentSlide=Math.max(0,Math.min(slides.length-1,currentSlide+d)); renderSlide(); renderDots(); }
function navTo(i) { currentSlide=i; renderSlide(); renderDots(); }

function download() {
    if(!pptBlob) return toast(t('createFirst'),'error');
    const a=document.createElement('a');
    a.href=URL.createObjectURL(pptBlob);
    a.download=`pres_${Date.now()}.pptx`;
    a.click();
    toast(t('downloaded'),'success');
}

function reset() {
    pptBlob=null; slides=[]; currentSlide=0;
    document.getElementById('stateEmpty').style.display='block';
    document.getElementById('stateSlides').style.display='none';
    document.getElementById('previewToolbar').style.display='none';
    switchStep(1);
    toast(t('formReset'),'info');
}

function setLoading(v) {
    document.getElementById('stateEmpty').style.display=v?'none':'block';
    document.getElementById('stateLoading').style.display=v?'block':'none';
    document.getElementById('stateSlides').style.display='none';
    const btn=document.getElementById('generateBtn');
    btn.querySelector('.btn-text').style.display=v?'none':'inline';
    btn.querySelector('.btn-loader').style.display=v?'flex':'none';
    btn.disabled=v;
}

function updateProgress(p,txt) { document.getElementById('progressFill').style.width=p+'%'; document.getElementById('loadingText').textContent=txt; }

function toast(msg,type='info') {
    const c=document.getElementById('toasts');
    const t=document.createElement('div');
    t.className=`toast ${type}`;
    t.textContent=msg;
    c.appendChild(t);
    setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),300);},4000);
}

function formatSize(b){return b<1024?b+' B':b<1024*1024?(b/1024).toFixed(1)+' KB':(b/1024/1024).toFixed(1)+' MB';}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}