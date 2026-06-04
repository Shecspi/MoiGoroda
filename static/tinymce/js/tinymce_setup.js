/**
 * Общий setup TinyMCE: подключает все кастомные расширения редактора.
 */
(function () {
  'use strict';

  function djangoTinyMCESetup(editor) {
    if (typeof window.djangoTinyMCESetupRtbBanner === 'function') {
      window.djangoTinyMCESetupRtbBanner(editor);
    }
    if (typeof window.djangoTinyMCESetupBlogCarousel === 'function') {
      window.djangoTinyMCESetupBlogCarousel(editor);
    }
  }

  window.djangoTinyMCESetup = djangoTinyMCESetup;
})();
