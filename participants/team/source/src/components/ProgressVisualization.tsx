import { motion } from 'framer-motion';
import { FileSearch, Brain, Image, Boxes, CheckCircle2 } from 'lucide-react';
import { GenerationStep } from '../App';

interface ProgressVisualizationProps {
  currentStep: GenerationStep;
  slideCount: number;
}

const steps = [
  { id: 'parsing', label: 'Парсинг документа', icon: FileSearch, color: '#0019B5' },
  { id: 'analyzing', label: 'AI-анализ контента', icon: Brain, color: '#7700C7' },
  { id: 'generating-images', label: 'Генерация изображений', icon: Image, color: '#FF4F12' },
  { id: 'building', label: 'Сборка презентации', icon: Boxes, color: '#0019B5' },
];

export default function ProgressVisualization({ currentStep, slideCount }: ProgressVisualizationProps) {
  const getCurrentStepIndex = () => {
    return steps.findIndex(s => s.id === currentStep);
  };

  const currentIndex = getCurrentStepIndex();

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0019B5] to-[#7700C7] p-8 text-white">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-center gap-3 mb-4"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Brain className="w-12 h-12" />
            </motion.div>
            <h2 className="text-3xl font-bold">Генерация презентации</h2>
          </motion.div>
          <p className="text-center text-blue-100 text-lg">
            Создаём {slideCount} профессиональных слайдов...
          </p>
        </div>

        {/* Progress Steps */}
        <div className="p-8">
          <div className="space-y-6">
            {steps.map((step, index) => {
              const isActive = index === currentIndex;
              const isCompleted = index < currentIndex;
              const Icon = step.icon;

              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  <div className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
                    isActive ? 'bg-gradient-to-r from-blue-50 to-purple-50 scale-105' : ''
                  }`}>
                    <div
                      className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                        isCompleted
                          ? 'bg-green-500'
                          : isActive
                          ? 'bg-gradient-to-br from-[#0019B5] to-[#7700C7] animate-pulse'
                          : 'bg-gray-200'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-7 h-7 text-white" />
                      ) : (
                        <Icon
                          className={`w-7 h-7 ${
                            isActive ? 'text-white' : 'text-gray-400'
                          }`}
                        />
                      )}
                    </div>

                    <div className="flex-1">
                      <h3 className={`font-bold text-lg ${
                        isActive ? 'text-[#0019B5]' : isCompleted ? 'text-gray-700' : 'text-gray-400'
                      }`}>
                        {step.label}
                      </h3>
                      {isActive && (
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: '100%' }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="h-1 bg-gradient-to-r from-[#0019B5] to-[#7700C7] rounded-full mt-2"
                        />
                      )}
                      {isCompleted && (
                        <p className="text-sm text-green-600 font-medium mt-1">
                          ✓ Завершено
                        </p>
                      )}
                    </div>

                    {isActive && (
                      <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-3 h-3 bg-[#FF4F12] rounded-full"
                      />
                    )}
                  </div>

                  {/* Connector Line */}
                  {index < steps.length - 1 && (
                    <div className="ml-7 h-6 w-0.5 bg-gray-200" />
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Fun Facts */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 border-t border-gray-200">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="flex items-start gap-3"
          >
            <div className="text-3xl">💡</div>
            <div>
              <p className="font-semibold text-gray-900 mb-1">Знаете ли вы?</p>
              <p className="text-sm text-gray-700">
                {currentStep === 'parsing' && 'Искусственный интеллект анализирует структуру вашего документа и выделяет ключевые темы.'}
                {currentStep === 'analyzing' && 'Нейросеть обрабатывает контент и создаёт оптимальную структуру слайдов с учётом лучших практик презентаций.'}
                {currentStep === 'generating-images' && 'Генеративные модели создают уникальные иллюстрации, соответствующие контенту каждого слайда.'}
                {currentStep === 'building' && 'Презентация собирается с применением фирменного стиля Ростелекома: цвета, шрифты и композиция.'}
              </p>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Animated Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-6 grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Слайдов', value: slideCount, icon: '📊' },
          { label: 'Этапов', value: `${currentIndex + 1}/${steps.length}`, icon: '⚙️' },
          { label: 'AI моделей', value: '3', icon: '🤖' },
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4 + idx * 0.1 }}
            className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 text-center"
          >
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold text-[#0019B5] mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
