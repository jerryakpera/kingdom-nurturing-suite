document.addEventListener('DOMContentLoaded', () => {
  const modalButtons = document.querySelectorAll(
    '[id^="open-group-modal-button-"]'
  );

  modalButtons.forEach((button) => {
    const groupId = button.id.split('-').pop();
    const modalId = `extralarge-modal-${groupId}`;
    const closeButtonId = `close-group-modal-button-${groupId}`;

    const $targetEl = document.getElementById(modalId);

    const options = {
      placement: 'bottom-right',
      backdrop: 'dynamic',
      backdropClasses:
        'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40 top-0 left-0 right-0',
      closable: true,
    };

    const modal = new Modal($targetEl, options);

    button.addEventListener('click', () => {
      modal.show();
    });

    document.getElementById(closeButtonId).addEventListener('click', () => {
      modal.hide();
    });
  });
});
