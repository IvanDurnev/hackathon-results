import { motion } from 'framer-motion';
import { Download, RotateCcw, FileText, Image as ImageIcon, Maximize2 } from 'lucide-react';
import { GenerationSettings } from '../App';
import { useState } from 'react';

interface GeneratorDashboardProps {
  slides: any[];
  onReset: () => void;
  settings: GenerationSettings;
}

export default function GeneratorDashboard({ slides, onReset, settings }: GeneratorDashboardProps) {
  const [selectedSlide, setSelectedSlide] = useState<number | null>(null);

  const handleDownload = () => {
    // В реальной системе здесь будет запрос на бекенд для генерации PPTX
    alert('В production версии здесь будет загрузка готовой презентации PPTX');
  };

  return (
    <div className="space-y-6">
      {/* Success Header */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center"
            >
              <span className="text-4xl">✨</span>
            </motion.div>
            <div>
              <h2 className="text-3xl font-bold mb-2">Презентация готова!</h2>
              <p className="text-green-100 text-lg">
                Создано {slides.length} профессиональных слайдов
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-6 py-3 bg-white text-green-600 rounded-xl font-semibold hover:shadow-lg transition-all hover:scale-105"
            >
              <Download className="w-5 h-5" />
              Скачать PPTX
            </button>
            <button
              onClick={onReset}
              className="flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-sm text-white rounded-xl font-semibold hover:bg-white/20 transition-all"
            >
              <RotateCcw className="w-5 h-5" />
              Создать новую
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Всего слайдов', value: slides.length, icon: FileText, color: 'from-blue-500 to-blue-600' },
          { label: 'С изображениями', value: slides.filter(s => s.image_prompt).length, icon: ImageIcon, color: 'from-purple-500 to-purple-600' },
          { label: 'Тон', value: settings.tone === 'official' ? 'Официальный' : 'Креативный', icon: '🎯', color: 'from-orange-500 to-orange-600' },
          { label: 'Цветовая схема', value: settings.colorScheme, icon: '🎨', color: 'from-pink-500 to-pink-600' },
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + idx * 0.1 }}
            className="bg-white rounded-xl shadow-lg border border-gray-200 p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              {typeof stat.icon === 'string' ? (
                <div className="text-2xl">{stat.icon}</div>
              ) : (
                <div className={`w-10 h-10 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center`}>
                  <stat.icon className="w-5 h-5 text-white" />
                </div>
              )}
              <div className="text-sm text-gray-600 font-medium">{stat.label}</div>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
          </motion.div>
        ))}
      </div>

      {/* Slides Preview Grid */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4">Предпросмотр слайдов</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {slides.map((slide, idx) => (
            <motion.div
              key={slide.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + idx * 0.05 }}
              onClick={() => setSelectedSlide(selectedSlide === idx ? null : idx)}
              className={`cursor-pointer group relative bg-white rounded-xl shadow-lg border-2 overflow-hidden transition-all hover:shadow-xl ${
                selectedSlide === idx ? 'border-[#0019B5] ring-4 ring-[#0019B5]/20' : 'border-gray-200 hover:border-[#0019B5]/50'
              }`}
            >
              {/* Slide Number Badge */}
              <div className="absolute top-2 left-2 z-10 w-8 h-8 bg-gradient-to-br from-[#0019B5] to-[#7700C7] rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {idx + 1}
              </div>

              {/* Slide Preview */}
              <div className={`aspect-[16/9] p-6 flex flex-col justify-center ${
                slide.type === 'title' 
                  ? 'bg-gradient-to-br from-[#0019B5] to-[#7700C7]'
                  : 'bg-gradient-to-br from-gray-50 to-gray-100'
              }`}>
                <div className={`text-center ${slide.type === 'title' ? 'text-white' : 'text-gray-900'}`}>
                  <h4 className="font-bold text-sm mb-2 line-clamp-2">
                    {slide.title}
                  </h4>
                  {slide.subtitle && (
                    <p className="text-xs opacity-80 line-clamp-1">{slide.subtitle}</p>
                  )}
                  {slide.content?.bullets && slide.content.bullets.length > 0 && (
                    <div className="mt-3 space-y-1">
                      {slide.content.bullets.slice(0, 2).map((bullet: string, i: number) => (
                        <div key={i} className="flex items-start gap-1 text-xs">
                          <span className={slide.type === 'title' ? 'text-white' : 'text-[#0019B5]'}>•</span>
                          <span className="line-clamp-1 text-left">{bullet}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Image Indicator */}
              {slide.image_prompt && (
                <div className="absolute bottom-2 right-2 bg-[#FF4F12] text-white rounded-full p-1.5 shadow-lg">
                  <ImageIcon className="w-3 h-3" />
                </div>
              )}

              {/* Hover Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center pb-3">
                <div className="flex items-center gap-1 text-white text-xs font-medium">
                  <Maximize2 className="w-3 h-3" />
                  <span>Просмотр</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Detailed Slide View */}
      {selectedSlide !== null && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-2xl border border-gray-200 p-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-900">
              Слайд {selectedSlide + 1}: {slides[selectedSlide].title}
            </h3>
            <button
              onClick={() => setSelectedSlide(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Preview */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-3">Превью:</h4>
              <div className={`aspect-[16/9] rounded-xl p-8 flex flex-col justify-center ${
                slides[selectedSlide].type === 'title'
                  ? 'bg-gradient-to-br from-[#0019B5] to-[#7700C7]'
                  : 'bg-gradient-to-br from-gray-50 to-gray-100'
              }`}>
                <div className={slides[selectedSlide].type === 'title' ? 'text-white' : 'text-gray-900'}>
                  <h2 className="text-2xl font-bold mb-2">{slides[selectedSlide].title}</h2>
                  {slides[selectedSlide].subtitle && (
                    <p className="text-lg opacity-80">{slides[selectedSlide].subtitle}</p>
                  )}
                  {slides[selectedSlide].content?.bullets && (
                    <ul className="mt-6 space-y-2">
                      {slides[selectedSlide].content.bullets.map((bullet: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className={slides[selectedSlide].type === 'title' ? 'text-white' : 'text-[#0019B5]'}>•</span>
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>

            {/* Details */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-3">Детали:</h4>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Тип слайда</div>
                  <div className="font-semibold text-gray-900 capitalize">{slides[selectedSlide].type}</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Лейаут</div>
                  <div className="font-semibold text-gray-900">{slides[selectedSlide].layout}</div>
                </div>
                {slides[selectedSlide].image_prompt && (
                  <div className="p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
                    <div className="text-sm text-orange-600 mb-2 flex items-center gap-2">
                      <ImageIcon className="w-4 h-4" />
                      Промпт для изображения
                    </div>
                    <div className="text-sm text-gray-700">{slides[selectedSlide].image_prompt}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Download Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
      >
        <div className="flex items-start gap-4">
          <div className="text-4xl">📦</div>
          <div className="flex-1">
            <h4 className="font-bold text-gray-900 mb-2">Что включено в скачиваемый файл:</h4>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>✓ Презентация в формате PPTX (PowerPoint)</li>
              <li>✓ Фирменные цвета и шрифты Ростелекома</li>
              <li>✓ Оптимизированная структура и контент</li>
              <li>✓ AI-сгенерированные иллюстрации (если включены)</li>
              <li>✓ Готовность к редактированию и презентации</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
