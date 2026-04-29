import { useState } from 'react';
import { Upload, FileText, Type, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface UploadZoneProps {
  onFileUpload: (file: File) => void;
  onTextInput: (text: string) => void;
  uploadedFile: File | null;
  textInput: string;
}

export default function UploadZone({ 
  onFileUpload, 
  onTextInput, 
  uploadedFile, 
  textInput 
}: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState<'file' | 'text'>('file');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || 
          file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
          file.type === 'text/plain') {
        onFileUpload(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('file')}
          className={`flex-1 px-6 py-4 font-medium transition-colors ${
            activeTab === 'file'
              ? 'bg-gradient-to-r from-[#0019B5]/10 to-[#7700C7]/10 text-[#0019B5] border-b-2 border-[#0019B5]'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <Upload className="w-5 h-5" />
            Загрузить файл
          </span>
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`flex-1 px-6 py-4 font-medium transition-colors ${
            activeTab === 'text'
              ? 'bg-gradient-to-r from-[#0019B5]/10 to-[#7700C7]/10 text-[#0019B5] border-b-2 border-[#0019B5]'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <Type className="w-5 h-5" />
            Ввести текст
          </span>
        </button>
      </div>

      <div className="p-8">
        {activeTab === 'file' ? (
          <div>
            {uploadedFile ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 bg-gradient-to-r from-[#0019B5]/5 to-[#7700C7]/5 rounded-xl border-2 border-[#0019B5]/20"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-[#0019B5] to-[#7700C7] rounded-lg flex items-center justify-center">
                      <FileText className="w-7 h-7 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{uploadedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(uploadedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => onFileUpload(null as any)}
                    className="p-2 hover:bg-white rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </motion.div>
            ) : (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                  dragActive
                    ? 'border-[#0019B5] bg-[#0019B5]/5'
                    : 'border-gray-300 hover:border-[#0019B5]/50'
                }`}
              >
                <input
                  type="file"
                  id="fileInput"
                  className="hidden"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                />
                <label
                  htmlFor="fileInput"
                  className="cursor-pointer flex flex-col items-center gap-4"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-[#0019B5] to-[#7700C7] rounded-full flex items-center justify-center">
                    <Upload className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900 mb-1">
                      Перетащите файл или нажмите для выбора
                    </p>
                    <p className="text-sm text-gray-600">
                      Поддерживаются форматы: PDF, DOCX, TXT (макс. 10 МБ)
                    </p>
                  </div>
                  <button
                    type="button"
                    className="mt-2 px-6 py-3 bg-gradient-to-r from-[#0019B5] to-[#7700C7] text-white rounded-lg font-medium hover:shadow-lg transition-shadow"
                  >
                    Выбрать файл
                  </button>
                </label>
              </div>
            )}
          </div>
        ) : (
          <div>
            <textarea
              value={textInput}
              onChange={(e) => onTextInput(e.target.value)}
              placeholder="Введите текст для генерации презентации... 

Например:
• Основная тема и цели презентации
• Ключевые разделы и тезисы
• Данные и статистика
• Выводы и рекомендации"
              className="w-full h-96 p-6 border-2 border-gray-300 rounded-xl focus:border-[#0019B5] focus:ring-2 focus:ring-[#0019B5]/20 outline-none resize-none text-gray-900 placeholder-gray-400"
            />
            <div className="mt-4 flex items-center justify-between text-sm">
              <span className="text-gray-600">
                Символов: {textInput.length}
              </span>
              {textInput.length > 0 && (
                <button
                  onClick={() => onTextInput('')}
                  className="text-[#FF4F12] hover:underline font-medium"
                >
                  Очистить
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6 bg-gray-50 border-t border-gray-200">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-[#0019B5]/10 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-sm mb-1">AI-анализ</h4>
            <p className="text-xs text-gray-600">Умная структуризация контента</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-[#7700C7]/10 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">🎨</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-sm mb-1">Фирменный стиль</h4>
            <p className="text-xs text-gray-600">Автоматическое применение брендинга</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-[#FF4F12]/10 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">⚡</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-sm mb-1">Быстро</h4>
            <p className="text-xs text-gray-600">Готовая презентация за минуту</p>
          </div>
        </div>
      </div>
    </div>
  );
}
