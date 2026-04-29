const API_BASE_URL = import.meta.env.DEV 
  ? '/api'  // В dev режиме используем прокси
  : (import.meta.env.VITE_API_BASE_URL || 'https://perfectly-agile-cobia.cloudpub.ru');

/**
 * Получение аналитического отчета по бюджету
 * @param {Object} params - Параметры запроса
 * @param {string} params.period_from - Начало периода (обязательно, формат: YYYY-MM)
 * @param {string} params.period_to - Конец периода (обязательно, формат: YYYY-MM)
 * @param {string} [params.kcsr_mask] - Маска КЦСР (обязательно если нет budget_name, для поиска только по дате указать "1")
 * @param {string} [params.budget_name] - Название бюджета (обязательно если нет kcsr_mask)
 * @param {string} [params.fund_source] - Источник финансирования
 * @param {number} [params.min_amount] - Минимальная сумма
 * @returns {Promise<Array>} Массив данных аналитики
 */
export async function getAnalyticsReport(params) {
  try {
    const queryParams = new URLSearchParams();
    
    // Добавляем параметры в query string
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const url = `${API_BASE_URL}/analytics/report?${queryParams.toString()}`;
    console.log('Fetching analytics report:', url);
    
    const response = await fetch(url, {
      method: 'GET',
    });

    if (!response.ok) {
      // Пытаемся получить детали ошибки от сервера
      let errorDetails = '';
      try {
        const errorData = await response.json();
        errorDetails = errorData.detail || errorData.message || JSON.stringify(errorData);
      } catch (e) {
        errorDetails = await response.text();
      }
      
      console.error('API Error Details:', {
        status: response.status,
        statusText: response.statusText,
        url: url,
        details: errorDetails
      });
      
      throw new Error(`HTTP error! status: ${response.status}, details: ${errorDetails}`);
    }

    const data = await response.json();
    console.log('Analytics report received:', data.length, 'records');
    return data;
  } catch (error) {
    console.error('Error fetching analytics report:', error);
    throw error;
  }
}

/**
 * Форматирование числа в валюту
 */
export function formatCurrency(value) {
  if (!value) return '0 ₽';
  const num = parseFloat(value);
  if (num >= 1000000000) {
    return `${(num / 1000000000).toFixed(1)} млрд ₽`;
  } else if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)} млн ₽`;
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)} тыс ₽`;
  }
  return `${num.toFixed(2)} ₽`;
}

/**
 * Форматирование даты из формата YYYY-MM
 */
export function formatPeriod(period) {
  if (!period) return '';
  const [year, month] = period.split('-');
  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];
  return `${monthNames[parseInt(month) - 1]} ${year}`;
}

/**
 * Экспорт данных в Excel
 * @param {Object} filters - Фильтры для экспорта
 * @returns {Promise<Object>} Результат экспорта
 */
export async function exportToExcel(filters = {}) {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  const url = `${API_BASE_URL}/analytics/export-excel?${params.toString()}`;
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Получаем blob для скачивания файла
    const blob = await response.blob();
    
    // Создаем ссылку для скачивания
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    
    // Получаем имя файла из заголовков или используем дефолтное
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'analytics_report.xlsx';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    throw error;
  }
}

/**
 * Генерация уникального session_id для пользователя
 * @returns {string} Уникальный идентификатор сессии
 */
export function generateSessionId() {
  // Проверяем есть ли уже session_id в localStorage
  let sessionId = localStorage.getItem('ai_session_id');
  
  if (!sessionId) {
    // Генерируем новый session_id
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('ai_session_id', sessionId);
  }
  
  return sessionId;
}

/**
 * Отправка вопроса AI ассистенту
 * @param {string} query - Вопрос пользователя
 * @param {string} sessionId - Идентификатор сессии
 * @returns {Promise<Object>} Ответ от AI
 */
export async function askAI(query, sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/ai/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI API Error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error asking AI:', error);
    throw error;
  }
}
