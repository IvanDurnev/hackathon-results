import { motion } from 'framer-motion';

interface SlidePreviewProps {
  slide: any;
  index: number;
}

export default function SlidePreview({ slide, index }: SlidePreviewProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-shadow"
    >
      <div className="aspect-[16/9] bg-gradient-to-br from-[#0019B5] to-[#7700C7] p-6 flex items-center justify-center">
        <div className="text-white text-center">
          <h3 className="text-lg font-bold mb-2">{slide.title}</h3>
          {slide.subtitle && <p className="text-sm opacity-90">{slide.subtitle}</p>}
        </div>
      </div>
      <div className="p-4">
        <div className="text-xs text-gray-500">Слайд {index + 1}</div>
      </div>
    </motion.div>
  );
}
