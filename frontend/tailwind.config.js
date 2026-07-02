/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sakura: {
          light: '#FFB7C5',
          DEFAULT: '#FF8FA3',
          dark: '#E0576F',
        },
        sky: {
          light: '#C5E8F7',
          DEFAULT: '#87CEEB',
          dark: '#4A90B8',
        },
        midnight: {
          light: '#2A2A4A',
          DEFAULT: '#1A1A2E',
          dark: '#0F0F23',
        },
        matcha: {
          light: '#C5D5B8',
          DEFAULT: '#8DB580',
          dark: '#5C8A4F',
        },
      },
      fontFamily: {
        sans: ['"PingFang SC"', '"Microsoft YaHei"', '"Noto Sans SC"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
      },
    },
  },
  plugins: [],
};
