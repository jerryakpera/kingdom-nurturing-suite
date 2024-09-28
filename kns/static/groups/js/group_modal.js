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
      closable: true,
      backdrop: 'dynamic',
      placement: 'top-right',
      backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
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
