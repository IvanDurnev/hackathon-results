import { useState } from 'react';
import { Sparkles, Settings, Zap, Presentation } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GeneratorDashboard from './components/GeneratorDashboard';
import UploadZone from './components/UploadZone';
import SettingsPanel from './components/SettingsPanel';
import ProgressVisualization from './components/ProgressVisualization';

export type GenerationSettings = {
  tone: 'official' | 'creative';
  slideCount: number;
  includeImages: boolean;
  colorScheme: 'blue' | 'purple' | 'gradient';
};

export type GenerationStep = 'idle' | 'parsing' | 'analyzing' | 'generating-images' | 'building' | 'complete';

function App() {
  const [currentStep, setCurrentStep] = useState<GenerationStep>('idle');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState<string>('');
  const [settings, setSettings] = useState<GenerationSettings>({
    tone: 'official',
    slideCount: 10,
    includeImages: true,
    colorScheme: 'gradient'
  });
  const [generatedSlides, setGeneratedSlides] = useState<any[]>([]);
  const [showSettings, setShowSettings] = useState(false);

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    setTextInput('');
  };

  const handleTextInput = (text: string) => {
    setTextInput(text);
    setUploadedFile(null);
  };

  const startGeneration = async () => {
    if (!uploadedFile && !textInput) return;

    // Симуляция процесса генерации
    setCurrentStep('parsing');
    await delay(1500);
    
    setCurrentStep('analyzing');
    await delay(2500);
    
    // Генерация mock слайдов
    const mockSlides = generateMockSlides(settings.slideCount);
    setGeneratedSlides(mockSlides);
    
    if (settings.includeImages) {
      setCurrentStep('generating-images');
      await delay(3000);
    }
    
    setCurrentStep('building');
    await delay(2000);
    
    setCurrentStep('complete');
  };

  const resetGeneration = () => {
    setCurrentStep('idle');
    setUploadedFile(null);
    setTextInput('');
    setGeneratedSlides([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#0019B5] to-[#7700C7] rounded-xl flex items-center justify-center">
                <Presentation className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-[#0019B5] to-[#7700C7] bg-clip-text text-transparent">
                  AI Генератор Презентаций
                </h1>
                <p className="text-sm text-gray-600">Powered by Ростелеком</p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Settings className="w-6 h-6 text-gray-700" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {currentStep === 'idle' ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Hero Section */}
              <div className="text-center mb-8">
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#0019B5]/10 to-[#7700C7]/10 rounded-full mb-4"
                >
                  <Zap className="w-4 h-4 text-[#FF4F12]" />
                  <span className="text-sm font-medium text-[#0019B5]">
                    Создайте профессиональную презентацию за минуту
                  </span>
                </motion.div>
                <h2 className="text-4xl font-bold text-gray-900 mb-3">
                  Загрузите документ или введите текст
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Искусственный интеллект проанализирует контент и создаст структурированную презентацию
                  в фирменном стиле Ростелекома
                </p>
              </div>

              {/* Settings Panel */}
              {showSettings && (
                <SettingsPanel settings={settings} onSettingsChange={setSettings} />
              )}

              {/* Upload Zone */}
              <UploadZone
                onFileUpload={handleFileUpload}
                onTextInput={handleTextInput}
                uploadedFile={uploadedFile}
                textInput={textInput}
              />

              {/* Generate Button */}
              {(uploadedFile || textInput) && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex justify-center"
                >
                  <button
                    onClick={startGeneration}
                    className="group relative px-8 py-4 bg-gradient-to-r from-[#0019B5] to-[#7700C7] text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all hover:scale-105"
                  >
                    <span className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5" />
                      Сгенерировать презентацию
                      <span className="text-sm opacity-80 ml-2">
                        (~{settings.slideCount} слайдов)
                      </span>
                    </span>
                  </button>
                </motion.div>
              )}
            </motion.div>
          ) : currentStep === 'complete' ? (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <GeneratorDashboard
                slides={generatedSlides}
                onReset={resetGeneration}
                settings={settings}
              />
            </motion.div>
          ) : (
            <motion.div
              key="progress"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <ProgressVisualization
                currentStep={currentStep}
                slideCount={settings.slideCount}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-600">
          <p className="text-sm">
            Разработано для хакатона Ростелеком 2026 | 
            <span className="mx-2">•</span>
            Powered by AI & Python
          </p>
        </div>
      </footer>
    </div>
  );
}

// Утилиты
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateMockSlides = (count: number) => {
  const slides = [];
  
  slides.push({
    id: 1,
    type: 'title',
    layout: 'title_only',
    title: 'Цифровая трансформация бизнеса',
    subtitle: 'Стратегия развития 2026-2028',
    content: { bullets: [], text: '' }
  });

  for (let i = 2; i <= count; i++) {
    slides.push({
      id: i,
      type: i === count ? 'conclusion' : 'content',
      layout: 'title_content',
      title: `Ключевой раздел ${i}`,
      content: {
        bullets: [
          'Анализ текущей ситуации на рынке',
          'Выявление ключевых трендов и возможностей',
          'Разработка стратегии внедрения',
          'Оценка рисков и планирование ресурсов'
        ],
        text: ''
      },
      image_prompt: i % 3 === 0 ? 'Modern technology abstract background' : null
    });
  }

  return slides;
};

export default App;
