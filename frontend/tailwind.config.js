const prelinePlugin = (() => {
  try {
    return require('preline/plugin');
  } catch (error) {
    console.warn('Preline Tailwind plugin не найден и будет пропущен:', error.message);
    return null;
  }
})();

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
      },
    },
  },
  darkMode: 'class',
  plugins: [
    prelinePlugin,
  ].filter(Boolean),
};
