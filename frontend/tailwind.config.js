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
          200: '#bfdbfe',
          400: '#60a5fa',
          500: '#3b82f6',
          800: '#1e40af',
        },
        secondary: {
          DEFAULT: '#e5e7eb',
          foreground: '#1f2937',
          100: '#f3f4f6',
          400: '#9ca3af',
          500: '#6b7280',
          800: '#1f2937',
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
        success: {
          DEFAULT: '#10b981',
          foreground: '#ffffff',
          100: '#d1fae5',
          200: '#a7f3d0',
          400: '#34d399',
          500: '#10b981',
          800: '#065f46',
        },
        info: {
          DEFAULT: '#0ea5e9',
          foreground: '#ffffff',
          100: '#e0f2fe',
          200: '#bae6fd',
          400: '#38bdf8',
          500: '#0ea5e9',
          800: '#075985',
        },
        warning: {
          DEFAULT: '#f59e0b',
          foreground: '#ffffff',
          100: '#fef3c7',
          200: '#fde68a',
          400: '#fbbf24',
          500: '#f59e0b',
          800: '#92400e',
        },
        danger: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff',
          100: '#fee2e2',
          200: '#fecaca',
          400: '#f87171',
          500: '#ef4444',
          800: '#991b1b',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
