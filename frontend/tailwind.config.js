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
    },
  },
  darkMode: 'class',
  plugins: [],
};
