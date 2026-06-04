/**
 * Одиночные изображения в TinyMCE (только админка): после вставки/загрузки — 200px по большей стороне
 * (как на странице статьи и в карусели).
 */
(function () {
  'use strict';

  var CONTENT_IMAGE_SIZE = 200;
  var SIZED_ATTR = 'data-mg-content-sized';
  var CAPTION_ATTR = 'data-mg-caption';

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

  function isStandaloneContentImage(img, editor) {
    return img && img.nodeName === 'IMG' && !editor.dom.getParent(img, '.mg-blog-carousel');
  }

  function clearImageFloatStyles(editor, img) {
    editor.dom.setStyle(img, 'float', null);
    editor.dom.setStyle(img, 'margin-left', null);
    editor.dom.setStyle(img, 'margin-right', null);
    var cls = img.className;
    if (!cls) {
      return;
    }
    var next = cls
      .replace(/\balign(left|center|right)\b/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    if (next) {
      img.className = next;
    } else {
      img.removeAttribute('class');
    }
  }

  function isLayoutBlock(node) {
    return node && (node.nodeName === 'P' || node.nodeName === 'DIV');
  }

  function isExcludedImageBlock(node) {
    if (!node || !node.classList) {
      return false;
    }
    return (
      node.classList.contains('mg-blog-carousel') ||
      node.classList.contains('ad-placeholder-rtb-banner')
    );
  }

  function getImageOnlyBlockImages(block, editor) {
    var imgs = [];
    var c;
    var node;

    for (c = 0; c < block.childNodes.length; c++) {
      node = block.childNodes[c];
      if (node.nodeType === 3) {
        if (node.nodeValue && node.nodeValue.trim()) {
          return null;
        }
        continue;
      }
      if (node.nodeType !== 1) {
        continue;
      }
      if (node.nodeName === 'BR') {
        continue;
      }
      if (node.nodeName === 'IMG' && isStandaloneContentImage(node, editor)) {
        imgs.push(node);
        continue;
      }
      return null;
    }

    return imgs.length ? imgs : null;
  }

  function wrapStandaloneImageInParagraph(editor, img) {
    if (!isStandaloneContentImage(img, editor)) {
      return false;
    }
    if (editor.dom.getParent(img, 'p,figure', true)) {
      return false;
    }

    var p = editor.dom.create('p');
    img.parentNode.insertBefore(p, img);
    p.appendChild(img);
    return true;
  }

  function splitStackedImagesInBlock(editor, block, imgs) {
    if (imgs.length <= 1) {
      return false;
    }

    var insertAfter = block;
    var i;
    var newP;

    if (block.nodeName === 'DIV') {
      var firstP = editor.dom.create('p');
      editor.dom.insertBefore(firstP, block);
      firstP.appendChild(imgs[0]);
      insertAfter = firstP;
    }

    for (i = 1; i < imgs.length; i++) {
      newP = editor.dom.create('p');
      editor.dom.insertAfter(newP, insertAfter);
      newP.appendChild(imgs[i]);
      insertAfter = newP;
    }

    if (block.nodeName === 'DIV') {
      editor.dom.remove(block);
    }

    return true;
  }

  function normalizeStandaloneImageLayout(editor) {
    var body = editor.getBody();
    if (!body) {
      return false;
    }

    var changed = false;
    var imgs = body.getElementsByTagName('img');
    var i;

    for (i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      if (!isStandaloneContentImage(img, editor)) {
        continue;
      }
      clearImageFloatStyles(editor, img);
      if (wrapStandaloneImageInParagraph(editor, img)) {
        changed = true;
      }
    }

    var blockList = [];
    var blocks = body.querySelectorAll('p, div');
    for (i = 0; i < blocks.length; i++) {
      if (!isLayoutBlock(blocks[i]) || isExcludedImageBlock(blocks[i])) {
        continue;
      }
      if (editor.dom.getParent(blocks[i], '.mg-blog-carousel')) {
        continue;
      }
      blockList.push(blocks[i]);
    }

    for (i = 0; i < blockList.length; i++) {
      var block = blockList[i];
      var blockImgs = getImageOnlyBlockImages(block, editor);
      if (!blockImgs) {
        continue;
      }
      var k;
      for (k = 0; k < blockImgs.length; k++) {
        clearImageFloatStyles(editor, blockImgs[k]);
      }
      if (splitStackedImagesInBlock(editor, block, blockImgs)) {
        changed = true;
      }
    }

    return changed;
  }

  function scanImageLayout(editor) {
    if (normalizeStandaloneImageLayout(editor)) {
      editor.nodeChanged();
      scanCaptionPreviews(editor);
    }
  }

  function syncCaptionPreview(editor, img) {
    if (!img || img.nodeName !== 'IMG') {
      return;
    }
    if (editor.dom.getParent(img, '.mg-blog-carousel')) {
      return;
    }

    var alt = (img.getAttribute('alt') || '').trim();
    var wrapper = editor.dom.getParent(img, 'p,figure', true);

    if (wrapper && !editor.dom.getParent(wrapper, '.mg-blog-carousel')) {
      if (alt) {
        editor.dom.setAttrib(wrapper, CAPTION_ATTR, alt);
      } else {
        editor.dom.setAttrib(wrapper, CAPTION_ATTR, null);
      }
      editor.dom.setAttrib(img, CAPTION_ATTR, null);
      return;
    }

    if (alt) {
      editor.dom.setAttrib(img, CAPTION_ATTR, alt);
    } else {
      editor.dom.setAttrib(img, CAPTION_ATTR, null);
    }
  }

  function scanCaptionPreviews(editor) {
    var body = editor.getBody();
    if (!body) {
      return;
    }

    var imgs = body.getElementsByTagName('img');
    for (var i = 0; i < imgs.length; i++) {
      syncCaptionPreview(editor, imgs[i]);
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
      syncCaptionPreview(editor, img);
    }
  }

  function schedulePostUploadResize(editor, uploadedUrl, knownWidth, knownHeight) {
    window.setTimeout(function () {
      scanUnsizedImages(editor, uploadedUrl, knownWidth, knownHeight);
    }, 100);
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
              syncCaptionPreview(editor, node);
            } else if (node.querySelectorAll) {
              var addedImgs = node.querySelectorAll('img');
              for (var k = 0; k < addedImgs.length; k++) {
                applyStandardSize(editor, addedImgs[k]);
                syncCaptionPreview(editor, addedImgs[k]);
              }
            }
          }
        }

        if (mutation.type === 'attributes' && mutation.target.nodeName === 'IMG') {
          if (mutation.attributeName === SIZED_ATTR) {
            continue;
          }
          if (mutation.attributeName === CAPTION_ATTR) {
            continue;
          }
          applyStandardSize(editor, mutation.target);
          if (mutation.attributeName === 'alt') {
            syncCaptionPreview(editor, mutation.target);
          }
        }
      }
    });

    observer.observe(body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['src', 'width', 'height', 'style', 'alt']
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

  function stripStandaloneCaptionAttrs(html) {
    var parser = new DOMParser();
    var doc = parser.parseFromString('<div id="mg-root">' + html + '</div>', 'text/html');
    var root = doc.getElementById('mg-root');
    if (!root) {
      return html;
    }

    var marked = root.querySelectorAll('[' + CAPTION_ATTR + ']');
    for (var i = 0; i < marked.length; i++) {
      var node = marked[i];
      if (node.classList && node.classList.contains('mg-blog-carousel')) {
        continue;
      }
      if (node.closest && node.closest('.mg-blog-carousel')) {
        continue;
      }
      node.removeAttribute(CAPTION_ATTR);
    }

    return root.innerHTML;
  }

  function djangoTinyMCESetupContentImage(editor) {
    installUploadHandlerOnEditor(editor);
    bindImageSizeObserver(editor);

    editor.on('PostProcess', function (e) {
      if (e.get && e.content) {
        e.content = stripStandaloneCaptionAttrs(e.content);
      }
    });

    var scanTimer = null;
    function scheduleScan() {
      if (scanTimer) {
        window.clearTimeout(scanTimer);
      }
      scanTimer = window.setTimeout(function () {
        scanTimer = null;
        scanUnsizedImages(editor);
        scanImageLayout(editor);
        scanCaptionPreviews(editor);
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
