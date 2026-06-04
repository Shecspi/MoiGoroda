/**
 * Кнопка TinyMCE «Карусель» в админке статей блога.
 * Зона загрузки повторяет разметку dropzone TinyMCE, input — свой с multiple.
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
      '" contenteditable="false" data-mg-blog-carousel>' +
      imgs +
      '</div><p></p>'
    );
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
      'Выбрано файлов: 0</p>' +
      '<p style="margin:4px 0 0;font-size:12px;color:rgba(34,47,62,.55);">' +
      'От ' +
      MIN_IMAGES +
      ' до ' +
      MAX_IMAGES +
      ' изображений. Можно выбрать несколько сразу (Ctrl+клик) или перетащить.</p>'
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
      countEl.textContent = 'Выбрано файлов: ' + selectedFiles.length + ' (макс. ' + MAX_IMAGES + ')';
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

  function djangoTinyMCESetupBlogCarousel(editor) {
    editor.ui.registry.addButton('blog_carousel', {
      text: 'Карусель',
      tooltip:
        'Вставить карусель из ' + MIN_IMAGES + '–' + MAX_IMAGES + ' фотографий',
      onAction: function () {
        var fileHolder = { state: null };
        var inputId = 'mg-carousel-input-' + String(Date.now());

        editor.windowManager.open({
          title: 'Карусель фотографий',
          size: 'normal',
          body: {
            type: 'panel',
            items: [
              {
                type: 'htmlpanel',
                html: buildDropzoneHtml(editor, inputId),
                onInit: function (el) {
                  bindFileSelection(el, fileHolder);
                }
              },
              {
                type: 'input',
                name: 'alt',
                label: 'Подпись (для всех фото)'
              }
            ]
          },
          buttons: [
            { type: 'cancel', text: 'Отмена' },
            { type: 'submit', text: 'Загрузить и вставить', primary: true }
          ],
          onOpen: function (api) {
            window.setTimeout(function () {
              if (!fileHolder.state) {
                bindFileSelection(api.getEl(), fileHolder);
              }
            }, 0);
          },
          onClose: function () {
            fileHolder.state = null;
          },
          onSubmit: function (api) {
            if (!fileHolder.state) {
              bindFileSelection(api.getEl(), fileHolder);
            }

            var fileinput = fileHolder.state ? fileHolder.state.getFiles() : [];

            if (!fileinput.length || fileinput.length < MIN_IMAGES) {
              editor.windowManager.alert(
                'Нужно выбрать минимум ' + MIN_IMAGES + ' изображения.'
              );
              return;
            }

            if (fileHolder.state && fileHolder.state.wasLimitExceeded()) {
              editor.windowManager.alert(
                'Выбрано больше ' +
                  MAX_IMAGES +
                  ' файлов — в карусель попадут только первые ' +
                  MAX_IMAGES +
                  '.'
              );
            }

            var alt = (api.getData().alt || '').trim();

            function setUploadProgress(percent) {
              api.block('Загрузка… ' + percent + '%');
            }

            setUploadProgress(0);
            uploadFiles(fileinput, setUploadProgress)
              .then(function (urls) {
                editor.insertContent(buildCarouselHtml(urls, alt));
                api.close();
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
    });
  }

  window.djangoTinyMCESetupBlogCarousel = djangoTinyMCESetupBlogCarousel;
})();
