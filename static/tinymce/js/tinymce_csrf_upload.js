/**
 * Обработчик загрузки изображений TinyMCE с отправкой CSRF-токена Django.
 * Подключается через TINYMCE_EXTRA_MEDIA и используется как images_upload_handler.
 */
(function () {
  'use strict';

  var UPLOAD_URL = '/tinymce/upload-image/';

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
  }

  function parseUploadResponse(xhr) {
    var data;
    try {
      data = JSON.parse(xhr.responseText);
    } catch (e) {
      return Promise.reject('Upload failed: invalid response');
    }
    if (data.location) {
      return Promise.resolve(data.location);
    }
    return Promise.reject(data.error || 'No location in response');
  }

  function uploadViaXhr(file, filename, onProgress) {
    var csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
      return Promise.reject('CSRF token not found');
    }

    return new Promise(function (resolve, reject) {
      var xhr = new XMLHttpRequest();
      var formData = new FormData();
      formData.append('file', file, filename || file.name || 'image.jpg');

      xhr.open('POST', UPLOAD_URL, true);
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.withCredentials = true;

      xhr.upload.onprogress = function (event) {
        if (!onProgress || !event.lengthComputable) {
          return;
        }
        onProgress(Math.round((event.loaded / event.total) * 100));
      };

      xhr.onload = function () {
        if (xhr.status < 200 || xhr.status >= 300) {
          reject('Upload failed: ' + xhr.status);
          return;
        }
        parseUploadResponse(xhr).then(resolve).catch(reject);
      };

      xhr.onerror = function () {
        reject('Upload failed: network error');
      };

      xhr.send(formData);
    });
  }

  function uploadViaFetch(file, filename) {
    var csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
      return Promise.reject('CSRF token not found');
    }

    var formData = new FormData();
    formData.append('file', file, filename || file.name || 'image.jpg');

    return fetch(UPLOAD_URL, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrftoken
      },
      credentials: 'same-origin'
    }).then(function (response) {
      if (!response.ok) {
        return response.json().then(function (data) {
          return Promise.reject(data.error || 'Upload failed');
        }).catch(function () {
          return Promise.reject('Upload failed: ' + response.status);
        });
      }
      return response.json();
    }).then(function (data) {
      if (data.location) {
        return data.location;
      }
      return Promise.reject('No location in response');
    });
  }

  /**
   * @param {Blob|File} file
   * @param {string} [filename]
   * @param {{ onProgress?: function(number): void }} [options]
   */
  function djangoTinyMCEUploadImageFile(file, filename, options) {
    var onProgress = options && typeof options.onProgress === 'function' ? options.onProgress : null;
    if (onProgress) {
      return uploadViaXhr(file, filename, onProgress);
    }
    return uploadViaFetch(file, filename);
  }

  function djangoTinyMCEImagesUploadHandler(blobInfo, progress) {
    var onProgress = typeof progress === 'function' ? progress : null;
    return djangoTinyMCEUploadImageFile(blobInfo.blob(), blobInfo.filename(), {
      onProgress: onProgress
    });
  }

  window.djangoTinyMCEUploadImageFile = djangoTinyMCEUploadImageFile;
  window.djangoTinyMCEImagesUploadHandler = djangoTinyMCEImagesUploadHandler;
})();
