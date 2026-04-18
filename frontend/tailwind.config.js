/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './js/**/*.{js,ts}',
    './css/**/*.{css,scss}',
    '../templates/**/*.html',
    '../**/templates/**/*.html',
    './node_modules/preline/dist/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        pacifico: ['Pacifico', 'cursive'],
        roboto: ['Roboto', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          foreground: '#ffffff',
          100: '#dbeafe',
          400: '#60a5fa',
          500: '#3b82f6',
          800: '#1e40af',
        },
        secondary: {
          DEFAULT: '#e5e7eb',
          foreground: '#1f2937',
        },
        surface: {
          DEFAULT: '#ffffff',
          foreground: '#111827',
          4: '#f3f4f6',
        },
        muted: {
          DEFAULT: '#f3f4f6',
          foreground: {
            1: '#6b7280',
          },
        },
        plain: '#111827',
        inverse: '#ffffff',
        foreground: {
          DEFAULT: '#111827',
          inverse: '#ffffff',
        },
        line: {
          5: '#d1d5db',
          8: '#e5e7eb',
          inverse: 'rgba(255, 255, 255, 0.25)',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
