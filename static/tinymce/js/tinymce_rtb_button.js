/**
 * Кнопка TinyMCE для вставки маркера рекламного блока в текст статьи.
 * Вставляется div с data-ad (комментарии TinyMCE при сохранении вырезает).
 * При выводе тег content_with_ads заменяет этот div на рекламный блок.
 */
(function () {
  'use strict';

  var PLACEHOLDER_HTML = '<div class="ad-placeholder-rtb-banner" data-ad="rtb_banner"></div>';

  function djangoTinyMCESetupRtbBanner(editor) {
    editor.ui.registry.addButton('rtb_banner', {
      text: 'Рекламный блок',
      tooltip: 'Вставить блок рекламы (будет отображаться при просмотре статьи)',
      onAction: function () {
        editor.insertContent(PLACEHOLDER_HTML);
      },
    });
  }

  window.djangoTinyMCESetupRtbBanner = djangoTinyMCESetupRtbBanner;
})();
