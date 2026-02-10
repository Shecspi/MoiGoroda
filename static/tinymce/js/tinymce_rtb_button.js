/**
 * Кнопки TinyMCE для вставки маркеров рекламных блоков в текст статьи.
 * Вставляется div с data-ad (комментарии TinyMCE при сохранении вырезает).
 * При выводе тег content_with_ads заменяет этот div на соответствующий рекламный блок.
 */
(function () {
  'use strict';

  var BUTTONS = [
    { id: 'rtb_banner_inside_article_1', text: 'Реклама 1', dataAd: 'rtb_banner_inside_article_1' },
    { id: 'rtb_banner_inside_article_2', text: 'Реклама 2', dataAd: 'rtb_banner_inside_article_2' },
    { id: 'rtb_banner_inside_article_3', text: 'Реклама 3', dataAd: 'rtb_banner_inside_article_3' },
  ];

  function djangoTinyMCESetupRtbBanner(editor) {
    BUTTONS.forEach(function (btn) {
      editor.ui.registry.addButton(btn.id, {
        text: btn.text,
        tooltip: 'Вставить ' + btn.text + ' (будет отображаться при просмотре статьи)',
        onAction: function () {
          editor.insertContent(
            '<div class="ad-placeholder-rtb-banner" data-ad="' + btn.dataAd + '"></div>'
          );
        },
      });
    });
  }

  window.djangoTinyMCESetupRtbBanner = djangoTinyMCESetupRtbBanner;
})();
