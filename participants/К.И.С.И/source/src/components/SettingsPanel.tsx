import { motion } from 'framer-motion';
import { Sliders, Palette, Image } from 'lucide-react';
import { GenerationSettings } from '../App';

interface SettingsPanelProps {
  settings: GenerationSettings;
  onSettingsChange: (settings: GenerationSettings) => void;
}

export default function SettingsPanel({ settings, onSettingsChange }: SettingsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-6"
    >
      <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Sliders className="w-5 h-5 text-[#0019B5]" />
        Настройки генерации
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tone Selection */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            Тон презентации
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => onSettingsChange({ ...settings, tone: 'official' })}
              className={`p-3 rounded-lg border-2 transition-all ${
                settings.tone === 'official'
                  ? 'border-[#0019B5] bg-[#0019B5]/5 text-[#0019B5]'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">🎯</div>
              <div className="text-xs font-medium">Официальный</div>
            </button>
            <button
              onClick={() => onSettingsChange({ ...settings, tone: 'creative' })}
              className={`p-3 rounded-lg border-2 transition-all ${
                settings.tone === 'creative'
                  ? 'border-[#7700C7] bg-[#7700C7]/5 text-[#7700C7]'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">✨</div>
              <div className="text-xs font-medium">Креативный</div>
            </button>
          </div>
        </div>

        {/* Slide Count */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            Количество слайдов: {settings.slideCount}
          </label>
          <input
            type="range"
            min="5"
            max="20"
            step="1"
            value={settings.slideCount}
            onChange={(e) => onSettingsChange({ ...settings, slideCount: parseInt(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#0019B5]"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>5</span>
            <span>20</span>
          </div>
        </div>

        {/* Color Scheme */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Palette className="w-4 h-4" />
            Цветовая схема
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => onSettingsChange({ ...settings, colorScheme: 'blue' })}
              className={`p-2 rounded-lg border-2 transition-all ${
                settings.colorScheme === 'blue'
                  ? 'border-[#0019B5] ring-2 ring-[#0019B5]/20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="w-full h-6 bg-[#0019B5] rounded"></div>
              <div className="text-xs mt-1 text-center font-medium">Синий</div>
            </button>
            <button
              onClick={() => onSettingsChange({ ...settings, colorScheme: 'purple' })}
              className={`p-2 rounded-lg border-2 transition-all ${
                settings.colorScheme === 'purple'
                  ? 'border-[#7700C7] ring-2 ring-[#7700C7]/20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="w-full h-6 bg-[#7700C7] rounded"></div>
              <div className="text-xs mt-1 text-center font-medium">Фиолетовый</div>
            </button>
            <button
              onClick={() => onSettingsChange({ ...settings, colorScheme: 'gradient' })}
              className={`p-2 rounded-lg border-2 transition-all ${
                settings.colorScheme === 'gradient'
                  ? 'border-[#0019B5] ring-2 ring-[#0019B5]/20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="w-full h-6 bg-gradient-to-r from-[#0019B5] to-[#7700C7] rounded"></div>
              <div className="text-xs mt-1 text-center font-medium">Градиент</div>
            </button>
          </div>
        </div>
      </div>

      {/* Include Images */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <label className="flex items-center gap-3 cursor-pointer group">
          <input
            type="checkbox"
            checked={settings.includeImages}
            onChange={(e) => onSettingsChange({ ...settings, includeImages: e.target.checked })}
            className="w-5 h-5 rounded border-gray-300 text-[#0019B5] focus:ring-[#0019B5]"
          />
          <div className="flex items-center gap-2">
            <Image className="w-5 h-5 text-[#0019B5]" />
            <span className="font-medium text-gray-900">
              Генерировать иллюстрации с помощью AI
            </span>
          </div>
        </label>
        <p className="text-sm text-gray-600 ml-8 mt-1">
          Создание релевантных изображений для визуализации контента
        </p>
      </div>
    </motion.div>
  );
}
