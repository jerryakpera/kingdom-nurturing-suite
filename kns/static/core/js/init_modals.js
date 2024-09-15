document.addEventListener('DOMContentLoaded', () => {
  // Reusable function to handle modal open and close events
  const initModal = (
    openButtonId,
    closeButtonId,
    modalElementId,
    userOptions = {}
  ) => {
    const openButton = document.getElementById(openButtonId);
    const closeButton = document.getElementById(closeButtonId);
    const $targetEl = document.getElementById(modalElementId);

    // Default modal options
    const defaultOptions = {
      placement: 'top-left',
      backdrop: 'dynamic',
      backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
      closable: true,
    };

    // Merge the default options with user-provided options
    const modalOptions = { ...defaultOptions, ...userOptions };

    const modal = new Modal($targetEl, modalOptions);

    // Add event listeners for opening and closing the modal
    openButton.addEventListener('click', () => modal.show());
    closeButton.addEventListener('click', () => modal.hide());
  };

  initModal(
    'open-filter-profiles-modal-button',
    'close-filter-profiles-modal-button',
    'filter-profiles-modal',
    {
      placement: 'top-left',
      backdrop: 'static', // Dynamic options for filter profiles modal
      closable: true,
    }
  );
});
