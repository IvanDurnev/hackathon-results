import { useState, useEffect, useRef } from 'react';
import { askAI, generateSessionId, formatCurrency, formatPeriod } from '../services/api';

// Компонент для отображения данных в виде таблицы
function DataTable({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="mt-2 sm:mt-3 overflow-x-auto -mx-3 sm:mx-0">
      <div className="bg-white rounded-lg sm:rounded-xl border border-[#E4EBF8] overflow-hidden min-w-[600px]">
        <table className="w-full text-[10px] sm:text-xs">
          <thead className="bg-[#F9FBFF]">
            <tr className="border-b border-[#E4EBF8]">
              <th className="text-left py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase">КЦСР</th>
              <th className="text-left py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase">Наименование</th>
              <th className="text-left py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase hidden md:table-cell">Бюджет</th>
              <th className="text-left py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase hidden sm:table-cell">Период</th>
              <th className="text-right py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase">Лимит ПБС</th>
              <th className="text-right py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase hidden lg:table-cell">Контракты</th>
              <th className="text-right py-2 px-2 sm:px-3 font-bold text-[#989FAC] uppercase">Оплачено</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 10).map((row, idx) => (
              <tr key={idx} className="border-b border-[#F4F5F7] hover:bg-[#F9FBFF]/50">
                <td className="py-2 px-2 sm:px-3 font-mono text-[#3772FE] font-bold break-all">{row.kcsr_code}</td>
                <td className="py-2 px-2 sm:px-3 text-[#0F172A] max-w-[150px] sm:max-w-xs truncate" title={row.kcsr_name}>
                  {row.kcsr_name}
                </td>
                <td className="py-2 px-2 sm:px-3 text-[#0F172A] hidden md:table-cell">{row.budget_name}</td>
                <td className="py-2 px-2 sm:px-3 text-[#989FAC] hidden sm:table-cell">{formatPeriod(row.budget_period)}</td>
                <td className="py-2 px-2 sm:px-3 text-right font-bold text-[#0F172A] break-all">
                  {formatCurrency(row.limit_pbs)}
                </td>
                <td className="py-2 px-2 sm:px-3 text-right font-bold text-[#0F172A] hidden lg:table-cell break-all">
                  {formatCurrency(row.gz_contracts_amount)}
                </td>
                <td className="py-2 px-2 sm:px-3 text-right font-bold text-[#31B96A] break-all">
                  {formatCurrency(row.gz_paid)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.length > 10 && (
          <div className="bg-[#F9FBFF] px-2 sm:px-3 py-2 text-center text-[#989FAC] text-[10px] sm:text-xs border-t border-[#E4EBF8]">
            Показано 10 из {data.length} записей
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('ru-RU');
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Загрузка истории чата из localStorage
  const loadChatHistory = () => {
    try {
      const savedMessages = localStorage.getItem('chat_messages');
      if (savedMessages) {
        const parsedMessages = JSON.parse(savedMessages);
        // Восстанавливаем объекты Date
        const messagesWithDates = parsedMessages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(messagesWithDates);
      } else {
        // Если истории нет, показываем приветственное сообщение
        const welcomeMessage = {
          type: 'bot',
          text: 'Здравствуйте! Я AI-ассистент для анализа бюджетных данных. Задайте мне вопрос об аналитике отчетов.',
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
        localStorage.setItem('chat_messages', JSON.stringify([welcomeMessage]));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Fallback к приветственному сообщению
      const welcomeMessage = {
        type: 'bot',
        text: 'Здравствуйте! Я AI-ассистент для анализа бюджетных данных. Задайте мне вопрос об аналитике отчетов.',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  };

  // Сохранение истории чата в localStorage
  const saveChatHistory = (newMessages) => {
    try {
      localStorage.setItem('chat_messages', JSON.stringify(newMessages));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  };

  // Начать новый чат
  const startNewChat = () => {
    // Генерируем новый session_id
    localStorage.removeItem('ai_session_id');
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    
    // Очищаем историю и добавляем приветственное сообщение
    const welcomeMessage = {
      type: 'bot',
      text: 'Здравствуйте! Я AI-ассистент для анализа бюджетных данных. Задайте мне вопрос об аналитике отчетов.',
      timestamp: new Date()
    };
    
    setMessages([welcomeMessage]);
    saveChatHistory([welcomeMessage]);
  };

  useEffect(() => {
    // Генерируем или получаем session_id при загрузке
    const id = generateSessionId();
    setSessionId(id);
    
    // Загружаем историю чата
    loadChatHistory();

    // Инициализация Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false; // Изменено на false - одна фраза за раз
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = selectedLanguage;
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started with language:', selectedLanguage);
        setIsListening(true);
        setIsProcessing(false);
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimText = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimText += transcript;
          }
        }

        // Обновляем финальный текст в поле ввода
        if (finalTranscript) {
          setInput(prev => prev + finalTranscript);
          setInterimTranscript('');
          setIsProcessing(false);
        }
        
        // Показываем промежуточный результат
        if (interimText) {
          setInterimTranscript(interimText);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        
        setIsListening(false);
        setIsProcessing(false);
        setInterimTranscript('');
        
        // Показываем сообщение об ошибке пользователю
        if (event.error === 'not-allowed') {
          alert('Доступ к микрофону запрещен. Пожалуйста, разрешите доступ в настройках браузера.');
        } else if (event.error === 'no-speech') {
          // Не показываем alert для no-speech, просто останавливаем
          console.log('No speech detected');
        } else if (event.error === 'network') {
          alert('Ошибка сети. Проверьте подключение к интернету.');
        } else if (event.error === 'aborted') {
          // Игнорируем aborted
          console.log('Recognition aborted');
        }
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
        // Если есть промежуточный текст, показываем что идет обработка
        if (interimTranscript) {
          setIsProcessing(true);
          // Через 2 секунды убираем индикатор обработки
          setTimeout(() => {
            setIsProcessing(false);
            setInterimTranscript('');
          }, 2000);
        } else {
          setIsProcessing(false);
          setInterimTranscript('');
        }
      };
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Игнорируем ошибки при остановке
        }
      }
    };
  }, [selectedLanguage]); // Добавляем selectedLanguage в зависимости

  useEffect(() => {
    // Автоскролл к последнему сообщению
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date()
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    saveChatHistory(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askAI(input, sessionId);
      
      // Проверяем, является ли ответ массивом данных или текстовым сообщением
      let botMessage;
      
      if (Array.isArray(response)) {
        // Если ответ - массив данных
        botMessage = {
          type: 'bot',
          text: `Найдено записей: ${response.length}`,
          data: response,
          timestamp: new Date()
        };
      } else if (response.message) {
        // Если ответ - объект с message
        botMessage = {
          type: 'bot',
          text: response.message,
          timestamp: new Date()
        };
      } else {
        // Неожиданный формат
        botMessage = {
          type: 'bot',
          text: JSON.stringify(response),
          timestamp: new Date()
        };
      }

      const updatedMessages = [...newMessages, botMessage];
      setMessages(updatedMessages);
      saveChatHistory(updatedMessages);
      
      // Обновляем session_id если он изменился
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
        localStorage.setItem('ai_session_id', response.session_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      let errorText = 'Извините, произошла ошибка при обработке вашего запроса.';
      
      if (error.message.includes('400')) {
        errorText = 'Некорректный запрос. Попробуйте переформулировать вопрос.';
      } else if (error.message.includes('404')) {
        errorText = 'Сервис AI временно недоступен. Попробуйте позже.';
      } else if (error.message.includes('500')) {
        errorText = 'Ошибка сервера. Попробуйте позже или начните новый чат.';
      } else if (error.message.includes('Failed to fetch')) {
        errorText = 'Проблема с подключением к серверу. Проверьте интернет-соединение.';
      }
      
      const errorMessage = {
        type: 'bot',
        text: errorText,
        timestamp: new Date(),
        isError: true
      };
      const updatedMessages = [...newMessages, errorMessage];
      setMessages(updatedMessages);
      saveChatHistory(updatedMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Распознавание речи не поддерживается в вашем браузере. Попробуйте использовать Chrome или Edge.');
      return;
    }

    if (isListening) {
      // Останавливаем запись, но показываем что идет обработка
      try {
        setIsProcessing(true);
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
        setIsProcessing(false);
      }
    } else {
      try {
        // Устанавливаем язык перед запуском
        recognitionRef.current.lang = selectedLanguage;
        console.log('Starting recognition with language:', selectedLanguage);
        
        setInterimTranscript('');
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        
        // Если уже запущено, сначала останавливаем
        if (error.message && error.message.includes('already started')) {
          try {
            recognitionRef.current.stop();
            setTimeout(() => {
              recognitionRef.current.lang = selectedLanguage;
              recognitionRef.current.start();
            }, 100);
          } catch (e) {
            console.error('Error restarting:', e);
            setIsListening(false);
            setIsProcessing(false);
          }
        } else {
          setIsListening(false);
          setIsProcessing(false);
        }
      }
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Заголовок чата */}
      <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm mb-3 sm:mb-4">
        <div className="flex items-center gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[#3772FE] to-[#A3C0FF] rounded-xl sm:rounded-2xl flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-black text-[#0F172A] text-base sm:text-lg">AI Ассистент</h3>
            <p className="text-[#989FAC] text-xs sm:text-sm truncate">Анализ бюджетных данных и отчетов</p>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <span className="text-[10px] sm:text-xs text-[#989FAC] font-mono hidden md:block">ID: {sessionId.slice(0, 20)}...</span>
            <button
              onClick={startNewChat}
              className="px-3 py-2 sm:px-4 sm:py-2 bg-[#F4F5F7] text-[#0F172A] rounded-xl font-bold text-xs sm:text-sm hover:bg-[#E4EBF8] transition-all flex items-center gap-1 sm:gap-2 flex-shrink-0"
              title="Начать новый чат"
            >
              <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">Новый чат</span>
            </button>
          </div>
        </div>
      </div>

      {/* Область сообщений */}
      <div className="flex-1 bg-white rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[90%] sm:max-w-[85%] rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 ${
                  message.type === 'user'
                    ? 'bg-[#3772FE] text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-[#F9FBFF] text-[#0F172A] border border-[#E4EBF8]'
                }`}
              >
                <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{message.text}</p>
                
                {/* Отображение таблицы с данными если есть */}
                {message.data && <DataTable data={message.data} />}
                
                <span className={`text-[9px] sm:text-[10px] mt-1 sm:mt-2 block ${
                  message.type === 'user' ? 'text-white/70' : 'text-[#989FAC]'
                }`}>
                  {message.timestamp.toLocaleTimeString('ru-RU', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[#F9FBFF] rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 border border-[#E4EBF8]">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[#3772FE] rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-[#3772FE] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-[#3772FE] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Поле ввода */}
        <div className="border-t border-[#E4EBF8] p-3 sm:p-4">
          <div className="flex gap-2 sm:gap-3">
            <div className="flex-1 relative min-w-0">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Задайте вопрос об аналитике бюджета..."
                className="w-full resize-none rounded-xl border border-[#E4EBF8] px-3 py-2 sm:px-4 sm:py-3 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-[#3772FE] focus:border-transparent"
                rows="2"
                disabled={isLoading}
              />
              {(isListening || isProcessing) && interimTranscript && (
                <div className="absolute bottom-2 left-3 sm:left-4 right-3 sm:right-4 text-[10px] sm:text-xs text-[#3772FE] italic opacity-70">
                  {interimTranscript}
                </div>
              )}
            </div>
            <div className="flex flex-col gap-2 flex-shrink-0">
              <button
                onClick={toggleVoiceInput}
                disabled={isLoading || isProcessing}
                className={`px-3 py-2 sm:px-4 sm:py-3 rounded-xl font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center ${
                  isListening
                    ? 'bg-red-500 text-white shadow-lg shadow-red-500/20 animate-pulse'
                    : isProcessing
                    ? 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/20'
                    : 'bg-[#F4F5F7] text-[#0F172A] hover:bg-[#E4EBF8]'
                }`}
                title={isListening ? 'Остановить запись' : isProcessing ? 'Обработка...' : 'Голосовой ввод'}
              >
                {isListening ? (
                  <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 6h12v12H6z" />
                  </svg>
                ) : isProcessing ? (
                  <svg className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                )}
              </button>
              
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="px-3 py-2 sm:px-4 sm:py-3 bg-[#3772FE] text-white rounded-xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                title="Отправить сообщение"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
          <p className="text-[10px] sm:text-xs text-[#989FAC] mt-2">
            {isListening ? (
              <span className="text-red-500 font-bold flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="hidden sm:inline">Слушаю... Говорите сейчас. Нажмите кнопку чтобы остановить.</span>
                <span className="sm:hidden">Слушаю...</span>
              </span>
            ) : isProcessing ? (
              <span className="text-yellow-600 font-bold flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-yellow-600 rounded-full animate-pulse"></span>
                <span className="hidden sm:inline">Обработка речи... Пожалуйста, подождите.</span>
                <span className="sm:hidden">Обработка...</span>
              </span>
            ) : (
              <span className="hidden sm:inline">Нажмите Enter для отправки, Shift+Enter для новой строки, или используйте микрофон</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
