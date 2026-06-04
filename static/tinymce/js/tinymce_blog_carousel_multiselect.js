/**
 * Кнопка TinyMCE «Карусель» в админке статей блога.
 * Вставка и редактирование блока .mg-blog-carousel.
 */
(function () {
  'use strict';

  var CAROUSEL_CLASS = 'mg-blog-carousel';
  var MIN_IMAGES = 2;
  var MAX_IMAGES = 10;
  var UPLOAD_CONCURRENCY = 3;
  var CONTENT_IMAGE_WIDTH = 500;

  function escapeAttr(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;');
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function buildCarouselHtml(urls, alt) {
    var altAttr = alt ? ' alt="' + escapeAttr(alt) + '"' : '';
    var captionAttr = alt ? ' data-mg-caption="' + escapeAttr(alt) + '"' : '';
    var imgs = urls
      .map(function (url) {
        return (
          '<img src="' +
          escapeAttr(url) +
          '" width="' +
          CONTENT_IMAGE_WIDTH +
          '"' +
          altAttr +
          '>'
        );
      })
      .join('');
    return (
      '<div class="' +
      CAROUSEL_CLASS +
      '" contenteditable="false" data-mg-blog-carousel' +
      captionAttr +
      '>' +
      imgs +
      '</div><p></p>'
    );
  }

  function parseCarouselElement(carouselEl) {
    var urls = [];
    var imgs = carouselEl.getElementsByTagName('img');
    for (var i = 0; i < imgs.length; i++) {
      var src = imgs[i].getAttribute('src');
      if (src) {
        urls.push(src);
      }
    }
    var alt = carouselEl.getAttribute('data-mg-caption') || '';
    if (!alt && imgs.length > 0) {
      alt = imgs[0].getAttribute('alt') || '';
    }
    return { urls: urls, alt: alt };
  }

  function findCarouselNode(node, editor) {
    if (!node) {
      return null;
    }
    if (node.nodeType === 1 && editor.dom.hasClass(node, CAROUSEL_CLASS)) {
      return node;
    }
    return editor.dom.getParent(node, '.' + CAROUSEL_CLASS);
  }

  function reportOverallProgress(done, total, filePercent, onProgress) {
    if (!onProgress || total <= 0) {
      return;
    }
    var base = (done / total) * 100;
    var slice = filePercent / total;
    onProgress(Math.min(100, Math.round(base + slice)));
  }

  function uploadSingleFile(file, done, total, onProgress) {
    return new Promise(function (resolve, reject) {
      window
        .djangoTinyMCEUploadImageFile(file, file.name, {
          onProgress: function (filePercent) {
            reportOverallProgress(done, total, filePercent, onProgress);
          }
        })
        .then(resolve)
        .catch(reject);
    });
  }

  function uploadFiles(files, onProgress) {
    if (!window.djangoTinyMCEUploadImageFile) {
      return Promise.reject('Загрузка изображений недоступна');
    }

    var total = files.length;
    var results = new Array(total);
    var nextIndex = 0;
    var completed = 0;

    function runWorker() {
      if (nextIndex >= total) {
        return Promise.resolve();
      }

      var index = nextIndex;
      nextIndex += 1;

      return uploadSingleFile(files[index], completed, total, onProgress)
        .then(function (url) {
          results[index] = url;
          completed += 1;
          reportOverallProgress(completed, total, 0, onProgress);
        })
        .then(runWorker);
    }

    var workers = [];
    var pool = Math.min(UPLOAD_CONCURRENCY, total);
    for (var i = 0; i < pool; i++) {
      workers.push(runWorker());
    }

    return Promise.all(workers).then(function () {
      return results;
    });
  }

  function filesToArray(fileList) {
    var arr = [];
    for (var i = 0; i < fileList.length; i++) {
      arr.push(fileList[i]);
    }
    return arr;
  }

  function fileKey(file) {
    return file.name + '|' + file.size + '|' + file.lastModified;
  }

  function mergeFiles(existing, incoming) {
    var seen = {};
    var result = [];
    var all = existing.concat(incoming);
    for (var i = 0; i < all.length; i++) {
      var key = fileKey(all[i]);
      if (!seen[key]) {
        seen[key] = true;
        result.push(all[i]);
      }
    }
    return result;
  }

  function buildExistingSlidesHtml(urls) {
    if (!urls.length) {
      return '';
    }
    var items = urls
      .map(function (url) {
        return (
          '<div class="mg-carousel-existing" data-mg-url="' +
          escapeAttr(url) +
          '" style="display:flex;align-items:center;gap:8px;margin:6px 0;">' +
          '<img src="' +
          escapeAttr(url) +
          '" alt="" style="width:64px;height:48px;object-fit:cover;border-radius:4px;flex-shrink:0;">' +
          '<span style="flex:1;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:rgba(34,47,62,.75);">' +
          escapeHtml(url) +
          '</span>' +
          '<button type="button" class="tox-button tox-button--secondary tox-button--naked" data-mg-remove-slide>Удалить</button>' +
          '</div>'
        );
      })
      .join('');
    return (
      '<div data-mg-existing-slides style="margin-bottom:12px;">' +
      '<p style="margin:0 0 6px;font-size:13px;font-weight:600;color:rgba(34,47,62,.85);">Текущие фото</p>' +
      items +
      '</div>'
    );
  }

  function buildDropzoneHtml(editor, inputId) {
    return (
      '<div class="tox-form__group tox-form__group--stretched">' +
      '<div class="tox-dropzone-container">' +
      '<div class="tox-dropzone" data-mg-carousel-dropzone>' +
      '<p>' +
      escapeHtml(editor.translate('Drop an image here')) +
      '</p>' +
      '<input type="file" id="' +
      escapeAttr(inputId) +
      '" data-mg-carousel-input accept="image/*" multiple tabindex="-1" ' +
      'style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">' +
      '<label for="' +
      escapeAttr(inputId) +
      '" class="tox-button tox-button--secondary" data-mg-carousel-browse>' +
      escapeHtml(editor.translate('Browse for an image')) +
      '</label>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<p data-mg-carousel-file-count style="margin:8px 0 0;font-size:13px;color:rgba(34,47,62,.7);">' +
      'Новых файлов: 0</p>' +
      '<p style="margin:4px 0 0;font-size:12px;color:rgba(34,47,62,.55);">' +
      'От ' +
      MIN_IMAGES +
      ' до ' +
      MAX_IMAGES +
      ' изображений в карусели. Можно выбрать несколько сразу (Ctrl+клик) или перетащить.</p>'
    );
  }

  function createFileSelectionState(rootEl) {
    var selectedFiles = [];
    var input = rootEl.querySelector('[data-mg-carousel-input]');
    var dropzone = rootEl.querySelector('[data-mg-carousel-dropzone]');
    var countEl = rootEl.querySelector('[data-mg-carousel-file-count]');
    var limitExceeded = false;

    function updateCount() {
      if (!countEl) {
        return;
      }
      countEl.textContent = 'Новых файлов: ' + selectedFiles.length;
    }

    function addFiles(fileList) {
      if (!fileList || !fileList.length) {
        return;
      }
      var merged = mergeFiles(selectedFiles, filesToArray(fileList));
      if (merged.length > MAX_IMAGES) {
        limitExceeded = true;
        merged = merged.slice(0, MAX_IMAGES);
      }
      selectedFiles = merged;
      updateCount();
    }

    if (!input) {
      return null;
    }

    input.multiple = true;
    input.setAttribute('multiple', 'multiple');
    input.addEventListener('change', function () {
      addFiles(input.files);
      input.value = '';
    });

    if (dropzone) {
      function setDragActive(active) {
        if (active) {
          dropzone.classList.add('dragenter');
        } else {
          dropzone.classList.remove('dragenter');
        }
      }

      dropzone.addEventListener('dragenter', function (e) {
        e.preventDefault();
        setDragActive(true);
      });
      dropzone.addEventListener('dragleave', function () {
        setDragActive(false);
      });
      dropzone.addEventListener('dragover', function (e) {
        e.preventDefault();
      });
      dropzone.addEventListener('drop', function (e) {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer && e.dataTransfer.files) {
          addFiles(e.dataTransfer.files);
        }
      });
    }

    return {
      getFiles: function () {
        return selectedFiles.slice();
      },
      wasLimitExceeded: function () {
        return limitExceeded;
      }
    };
  }

  function bindFileSelection(rootEl, holder) {
    holder.state = createFileSelectionState(rootEl);
    return Boolean(holder.state);
  }

  function findNodeUp(startNode, rootEl, attrName) {
    var node = startNode;
    while (node && node !== rootEl) {
      if (node.nodeType === 1 && node.getAttribute && node.getAttribute(attrName) !== null) {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  }

  function collectExistingUrls(panelEl) {
    if (!panelEl) {
      return [];
    }
    var container = panelEl.querySelector('[data-mg-existing-slides]') || panelEl;
    var urls = [];
    var rows = container.querySelectorAll('[data-mg-url]');
    for (var i = 0; i < rows.length; i++) {
      var url = rows[i].getAttribute('data-mg-url');
      if (url) {
        urls.push(url);
      }
    }
    return urls;
  }

  function bindExistingSlides(panelEl) {
    if (!panelEl || panelEl.getAttribute('data-mg-slides-bound') === 'true') {
      return;
    }
    panelEl.setAttribute('data-mg-slides-bound', 'true');

    panelEl.addEventListener('click', function (e) {
      var btn = findNodeUp(e.target, panelEl, 'data-mg-remove-slide');
      if (!btn) {
        return;
      }
      e.preventDefault();
      e.stopPropagation();

      var row = findNodeUp(btn, panelEl, 'data-mg-url');
      if (row && row.parentNode) {
        row.parentNode.removeChild(row);
      }
    });
  }

  function openCarouselDialog(editor, options) {
    options = options || {};
    var isEdit = Boolean(options.editNode);
    var editNode = options.editNode || null;
    var parsed = isEdit && editNode ? parseCarouselElement(editNode) : { urls: [], alt: '' };

    var fileHolder = { state: null };
    var dialogUi = { existingPanelEl: null, dropzonePanelEl: null };
    var inputId = 'mg-carousel-input-' + String(Date.now());
    var panelItems = [];

    if (isEdit) {
      panelItems.push({
        type: 'htmlpanel',
        html: buildExistingSlidesHtml(parsed.urls),
        onInit: function (el) {
          dialogUi.existingPanelEl = el;
          bindExistingSlides(el);
        }
      });
    }

    panelItems.push(
      {
        type: 'htmlpanel',
        html: buildDropzoneHtml(editor, inputId),
        onInit: function (el) {
          dialogUi.dropzonePanelEl = el;
          bindFileSelection(el, fileHolder);
        }
      },
      {
        type: 'input',
        name: 'alt',
        label: 'Подпись (для всех фото)'
      }
    );

    editor.windowManager.open({
      title: isEdit ? 'Изменить карусель' : 'Карусель фотографий',
      size: 'normal',
      body: {
        type: 'panel',
        items: panelItems
      },
      initialData: {
        alt: parsed.alt
      },
      buttons: [
        { type: 'cancel', text: 'Отмена' },
        {
          type: 'submit',
          text: isEdit ? 'Сохранить' : 'Загрузить и вставить',
          primary: true
        }
      ],
      onOpen: function () {
        window.setTimeout(function () {
          if (!fileHolder.state && dialogUi.dropzonePanelEl) {
            bindFileSelection(dialogUi.dropzonePanelEl, fileHolder);
          }
          if (isEdit && dialogUi.existingPanelEl) {
            bindExistingSlides(dialogUi.existingPanelEl);
          }
        }, 0);
      },
      onClose: function () {
        fileHolder.state = null;
        dialogUi.existingPanelEl = null;
        dialogUi.dropzonePanelEl = null;
      },
      onSubmit: function (api) {
        if (!fileHolder.state && dialogUi.dropzonePanelEl) {
          bindFileSelection(dialogUi.dropzonePanelEl, fileHolder);
        }

        var existingUrls = isEdit ? collectExistingUrls(dialogUi.existingPanelEl) : [];
        var newFiles = fileHolder.state ? fileHolder.state.getFiles() : [];
        var totalCount = existingUrls.length + newFiles.length;

        if (totalCount < MIN_IMAGES) {
          editor.windowManager.alert(
            'В карусели должно быть минимум ' + MIN_IMAGES + ' изображения.'
          );
          return;
        }

        if (totalCount > MAX_IMAGES) {
          editor.windowManager.alert(
            'В карусели может быть не более ' + MAX_IMAGES + ' изображений.'
          );
          return;
        }

        if (fileHolder.state && fileHolder.state.wasLimitExceeded()) {
          editor.windowManager.alert(
            'Выбрано больше ' +
              MAX_IMAGES +
              ' новых файлов — будут загружены только первые ' +
              MAX_IMAGES +
              '.'
          );
        }

        var alt = (api.getData().alt || '').trim();

        function setUploadProgress(percent) {
          api.block(isEdit ? 'Сохранение… ' + percent + '%' : 'Загрузка… ' + percent + '%');
        }

        function finish(urls) {
          if (isEdit && editNode) {
            editor.undoManager.transact(function () {
              editor.dom.setOuterHTML(editNode, buildCarouselHtml(urls, alt));
            });
          } else {
            editor.insertContent(buildCarouselHtml(urls, alt));
          }
          api.close();
        }

        if (!newFiles.length) {
          finish(existingUrls);
          return;
        }

        setUploadProgress(0);
        uploadFiles(newFiles, setUploadProgress)
          .then(function (uploadedUrls) {
            finish(existingUrls.concat(uploadedUrls));
          })
          .catch(function (err) {
            api.unblock();
            var message =
              typeof err === 'string' ? err : err && err.message ? err.message : 'Ошибка загрузки';
            editor.windowManager.alert(message);
          });
      }
    });
  }

  function djangoTinyMCESetupBlogCarousel(editor) {
    editor.ui.registry.addButton('blog_carousel', {
      text: 'Карусель',
      tooltip: 'Вставить карусель из ' + MIN_IMAGES + '–' + MAX_IMAGES + ' фотографий',
      onAction: function () {
        openCarouselDialog(editor, {});
      }
    });

    editor.ui.registry.addButton('blog_carousel_edit', {
      text: 'Изменить карусель',
      tooltip: 'Изменить выбранную карусель фотографий',
      onAction: function () {
        var carousel = findCarouselNode(editor.selection.getNode(), editor);
        if (!carousel) {
          editor.windowManager.alert('Выберите карусель в тексте статьи.');
          return;
        }
        openCarouselDialog(editor, { editNode: carousel });
      }
    });

    editor.ui.registry.addContextToolbar('mgBlogCarouselToolbar', {
      predicate: function (node) {
        return Boolean(findCarouselNode(node, editor));
      },
      items: 'blog_carousel_edit',
      position: 'node',
      scope: 'node'
    });

    editor.on('dblclick', function (event) {
      var carousel = findCarouselNode(event.target, editor);
      if (carousel) {
        event.preventDefault();
        openCarouselDialog(editor, { editNode: carousel });
      }
    });
  }

  window.djangoTinyMCESetupBlogCarousel = djangoTinyMCESetupBlogCarousel;
})();
