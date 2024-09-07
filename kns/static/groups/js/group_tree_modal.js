document.addEventListener('DOMContentLoaded', () => {
  const modalButton = document.getElementById('open-group-tree-modal-button');

  const modalId = 'group-tree-modal';
  const closeButtonId = 'close-group-tree-modal-button';

  const $targetEl = document.getElementById(modalId);

  const options = {
    closable: true,
    backdrop: 'dynamic',
    placement: 'top-left',
    backdropClasses: 'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40',
  };

  const modal = new Modal($targetEl, options);

  modalButton.addEventListener('click', () => {
    modal.show();
  });

  document.getElementById(closeButtonId).addEventListener('click', () => {
    modal.hide();
  });
});
