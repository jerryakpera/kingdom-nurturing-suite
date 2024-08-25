document.addEventListener('DOMContentLoaded', () => {
  const openButton = document.getElementById('open-consent-form-modal');
  const closeButton = document.getElementById('close-consent-form-modal');

  const $targetEl = document.getElementById('consent-form-modal');

  const options = {
    placement: 'bottom-right',
    backdrop: 'dynamic',
    backdropClasses: 'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40',
    closable: true,
  };

  const modal = new Modal($targetEl, options);

  openButton.addEventListener('click', () => {
    modal.show();
  });

  closeButton.addEventListener('click', () => {
    modal.hide();
  });
});
