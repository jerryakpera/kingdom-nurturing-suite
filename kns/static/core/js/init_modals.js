document.addEventListener('DOMContentLoaded', () => {
  // Reusable function to handle modal open and close events
  window.initModal = (
    openButtonId,
    closeButtonId,
    modalElementId,
    userOptions = {}
  ) => {
    const openButton = document.getElementById(openButtonId);
    const closeButton = document.getElementById(closeButtonId);
    const $targetEl = document.getElementById(modalElementId);

    if (!openButton || !closeButton || !$targetEl) {
      return;
    }

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
});
