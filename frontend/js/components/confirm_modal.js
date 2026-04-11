import { HSOverlay } from 'preline';

/**
 * Универсальное модальное окно подтверждения (разметка: templates/parts/confirm_modal.html).
 *
 * @param {object} [options]
 * @param {string} [options.title]
 * @param {string} [options.message]
 * @param {string} [options.confirmLabel]
 * @param {string} [options.cancelLabel]
 * @returns {Promise<boolean>} true — пользователь подтвердил, false — отмена или закрытие
 */
export function openConfirmModal(options = {}) {
  const modal = document.getElementById('confirm-action-modal');
  const acceptBtn = document.getElementById('confirm-action-modal-accept');
  if (!modal || !acceptBtn) {
    return Promise.resolve(false);
  }

  const titleEl = document.getElementById('confirm-action-modal-title');
  const messageEl = document.getElementById('confirm-action-modal-message');
  const cancelBtn = document.getElementById('confirm-action-modal-cancel');

  if (titleEl) {
    titleEl.textContent = options.title ?? 'Подтверждение';
  }
  if (messageEl) {
    messageEl.textContent = options.message ?? '';
  }
  acceptBtn.textContent = options.confirmLabel ?? 'Подтвердить';
  if (cancelBtn) {
    cancelBtn.textContent = options.cancelLabel ?? 'Отмена';
  }

  return new Promise((resolve) => {
    let settled = false;
    let userConfirmed = false;

    const finish = (value) => {
      if (settled) {
        return;
      }
      settled = true;
      resolve(value);
    };

    const onAccept = (e) => {
      e.preventDefault();
      userConfirmed = true;
      finish(true);
      closeConfirmModal();
    };

    const onClose = () => {
      modal.removeEventListener('close.hs.overlay', onClose);
      acceptBtn.removeEventListener('click', onAccept);
      if (!userConfirmed) {
        finish(false);
      }
      userConfirmed = false;
    };

    acceptBtn.addEventListener('click', onAccept);
    modal.addEventListener('close.hs.overlay', onClose);

    HSOverlay.open('#confirm-action-modal');
  });
}

function closeConfirmModal() {
  const modal = document.getElementById('confirm-action-modal');
  const closeBtn = modal?.querySelector('[data-hs-overlay="#confirm-action-modal"]');
  closeBtn?.click();
}
