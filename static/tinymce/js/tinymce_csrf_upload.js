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

  function djangoTinyMCEImagesUploadHandler(blobInfo, progress) {
    var csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
      return Promise.reject('CSRF token not found');
    }

    var formData = new FormData();
    formData.append('file', blobInfo.blob(), blobInfo.filename());

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

  window.djangoTinyMCEImagesUploadHandler = djangoTinyMCEImagesUploadHandler;
})();
