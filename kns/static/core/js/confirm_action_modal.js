document.addEventListener('DOMContentLoaded', function () {
  const closeButton = document.getElementById('close-confirm-modal-button');

  const confirmMessage = document.getElementById(
    'confirm-action-modal-message'
  );
  const yesButton = document.getElementById('confirm-action-modal-yes');
  const noButton = document.getElementById('confirm-action-modal-no');

  // Default modal options
  const defaultOptions = {
    placement: 'top-left',
    backdrop: 'dynamic',
    backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
    closable: true,
  };

  const $targetEl = document.getElementById('confirm-action-modal');
  const modal = new Modal($targetEl, defaultOptions);

  // Add event listeners for opening and closing the modal
  // Array.from(openButtons).forEach((openButton) => {
  //   openButton.addEventListener('click', () => modal.show());
  // });

  closeButton.addEventListener('click', () => modal.hide());

  let confirmUrl = null;

  // Bind click events to "Yes" and "No" buttons
  yesButton.addEventListener('click', function () {
    if (confirmUrl) {
      window.location.href = confirmUrl;
    }
    modal.hide();
  });

  noButton.addEventListener('click', function () {
    modal.hide();
  });

  // Function to show the modal
  function populateModalContent(message, url) {
    confirmMessage.textContent = message;
    confirmUrl = url;
  }

  // Bind event listeners to all links with `data-confirm-url`
  document.querySelectorAll('[data-confirm-url]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();

      const message = link.getAttribute('data-confirm-message');
      const url = link.getAttribute('data-confirm-url');

      modal.show();
      populateModalContent(message, url);
    });
  });
});
