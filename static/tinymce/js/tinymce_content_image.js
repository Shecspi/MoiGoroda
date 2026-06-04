/**
 * Одиночные изображения в TinyMCE (только админка): после вставки/загрузки — 200px по большей стороне
 * (как на странице статьи и в карусели).
 */
(function () {
  'use strict';

  var CONTENT_IMAGE_SIZE = 200;
  var SIZED_ATTR = 'data-mg-content-sized';

  function shouldResize(img, editor) {
    if (!img || img.nodeName !== 'IMG') {
      return false;
    }
    if (editor.dom.getParent(img, '.mg-blog-carousel')) {
      return false;
    }
    if (img.getAttribute(SIZED_ATTR) === 'true') {
      return false;
    }
    return true;
  }

  function commitStandardSize(editor, img, naturalWidth, naturalHeight) {
    if (!naturalWidth || !naturalHeight) {
      return false;
    }

    editor.dom.setAttrib(img, 'style', null);
    editor.dom.setAttrib(img, 'width', null);
    editor.dom.setAttrib(img, 'height', null);

    if (naturalHeight > naturalWidth) {
      editor.dom.setAttrib(img, 'height', String(CONTENT_IMAGE_SIZE));
      editor.dom.setAttrib(
        img,
        'style',
        'height: ' + CONTENT_IMAGE_SIZE + 'px; width: auto; max-width: 100%;'
      );
    } else {
      editor.dom.setAttrib(img, 'width', String(CONTENT_IMAGE_SIZE));
      editor.dom.setAttrib(
        img,
        'style',
        'width: ' + CONTENT_IMAGE_SIZE + 'px; height: auto; max-width: 100%;'
      );
    }

    editor.dom.setAttrib(img, SIZED_ATTR, 'true');
    return true;
  }

  function applyStandardSize(editor, img, knownWidth, knownHeight) {
    if (!shouldResize(img, editor)) {
      return;
    }

    var naturalWidth = knownWidth || img.naturalWidth;
    var naturalHeight = knownHeight || img.naturalHeight;

    if (commitStandardSize(editor, img, naturalWidth, naturalHeight)) {
      editor.nodeChanged();
      return;
    }

    function onLoad() {
      if (shouldResize(img, editor)) {
        if (commitStandardSize(editor, img, img.naturalWidth, img.naturalHeight)) {
          editor.nodeChanged();
        }
      }
    }

    img.addEventListener('load', onLoad, { once: true });

    if (img.complete && img.naturalWidth && img.naturalHeight) {
      onLoad();
    }
  }

  function urlMatches(imgSrc, uploadedUrl) {
    if (!imgSrc || !uploadedUrl) {
      return false;
    }
    if (imgSrc === uploadedUrl) {
      return true;
    }
    try {
      return imgSrc === new URL(uploadedUrl, window.location.href).href;
    } catch (e) {
      return imgSrc.indexOf(uploadedUrl) !== -1 || uploadedUrl.indexOf(imgSrc) !== -1;
    }
  }

  function scanUnsizedImages(editor, matchUrl, knownWidth, knownHeight) {
    var body = editor.getBody();
    if (!body) {
      return;
    }

    var imgs = body.getElementsByTagName('img');
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      if (matchUrl && !urlMatches(img.src, matchUrl)) {
        continue;
      }
      applyStandardSize(editor, img, knownWidth, knownHeight);
    }
  }

  function schedulePostUploadResize(editor, uploadedUrl, knownWidth, knownHeight) {
    var delays = [0, 30, 100, 250, 500, 1000];
    for (var d = 0; d < delays.length; d++) {
      (function (delay) {
        window.setTimeout(function () {
          scanUnsizedImages(editor, uploadedUrl, knownWidth, knownHeight);
        }, delay);
      })(delays[d]);
    }
  }

  function getOriginalUploadHandler() {
    var handler = window.djangoTinyMCEImagesUploadHandler;
    if (handler && handler.__mgOriginal) {
      return handler.__mgOriginal;
    }
    return handler;
  }

  function createUploadHandler(editor) {
    return function (blobInfo, progress) {
      var knownWidth = typeof blobInfo.width === 'function' ? blobInfo.width() : 0;
      var knownHeight = typeof blobInfo.height === 'function' ? blobInfo.height() : 0;

      return getOriginalUploadHandler()(blobInfo, progress).then(function (url) {
        schedulePostUploadResize(editor, url, knownWidth, knownHeight);
        return url;
      });
    };
  }

  function bindImageSizeObserver(editor) {
    var body = editor.getBody();
    if (!body || body.getAttribute('data-mg-img-observer') === 'true') {
      return;
    }
    body.setAttribute('data-mg-img-observer', 'true');

    var observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var mutation = mutations[i];

        if (mutation.type === 'childList') {
          for (var j = 0; j < mutation.addedNodes.length; j++) {
            var node = mutation.addedNodes[j];
            if (!node || node.nodeType !== 1) {
              continue;
            }
            if (node.nodeName === 'IMG') {
              applyStandardSize(editor, node);
            } else if (node.querySelectorAll) {
              var addedImgs = node.querySelectorAll('img');
              for (var k = 0; k < addedImgs.length; k++) {
                applyStandardSize(editor, addedImgs[k]);
              }
            }
          }
        }

        if (mutation.type === 'attributes' && mutation.target.nodeName === 'IMG') {
          if (mutation.attributeName === SIZED_ATTR) {
            continue;
          }
          applyStandardSize(editor, mutation.target);
        }
      }
    });

    observer.observe(body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['src', 'width', 'height', 'style']
    });
  }

  function installUploadHandlerOnEditor(editor) {
    if (!window.djangoTinyMCEImagesUploadHandler) {
      return;
    }
    if (!window.djangoTinyMCEImagesUploadHandler.__mgOriginal) {
      window.djangoTinyMCEImagesUploadHandler.__mgOriginal =
        window.djangoTinyMCEImagesUploadHandler;
    }

    var handler = createUploadHandler(editor);
    if (typeof editor.options !== 'undefined' && typeof editor.options.set === 'function') {
      editor.options.set('images_upload_handler', handler);
    } else if (editor.settings) {
      editor.settings.images_upload_handler = handler;
    }
  }

  function djangoTinyMCESetupContentImage(editor) {
    installUploadHandlerOnEditor(editor);
    bindImageSizeObserver(editor);

    var scanTimer = null;
    function scheduleScan() {
      if (scanTimer) {
        window.clearTimeout(scanTimer);
      }
      scanTimer = window.setTimeout(function () {
        scanTimer = null;
        scanUnsizedImages(editor);
      }, 30);
    }

    editor.on('SetContent', scheduleScan);
    editor.on('Change', scheduleScan);

    editor.on('ObjectResized', function (event) {
      var target = event && event.target;
      if (target && target.nodeName === 'IMG') {
        editor.dom.setAttrib(target, SIZED_ATTR, 'true');
      }
    });

    editor.on('init', function () {
      bindImageSizeObserver(editor);
      scheduleScan();
    });
  }

  window.djangoTinyMCESetupContentImage = djangoTinyMCESetupContentImage;
})();
