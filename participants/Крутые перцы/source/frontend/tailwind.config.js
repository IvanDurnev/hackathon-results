// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        panel: {
          dark: '#171A20',
          deep: '#0F172A',
          text: '#56607A',
          gray: '#7E8594',
          light: '#EAECF0',
          accent: '#3772FE',
          active: '#1D4ED8',
        },
        surface: {
          bg: '#F8F9FB',
          card: '#FBFCFE',
          border: '#E2E8F0',
        }
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(180deg, #FFFFFF 0%, #F9FBFF 100%)',
        'primary-gradient': 'linear-gradient(90deg, #5B8FFE 0%, #A3C0FF 100%)',
        'success-gradient': 'linear-gradient(90deg, #31B96A 0%, #7DDDA4 100%)',
        'surface-gradient': 'linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 100%)',
      }
    },
  },
}