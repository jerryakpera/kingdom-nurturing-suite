document.addEventListener('DOMContentLoaded', () => {
  initModal(
    'open-consent-form-modal',
    'close-consent-form-modal',
    'consent-form-modal',
    {
      placement: 'top-left',
      backdrop: 'static',
      backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
      closable: true,
    }
  );
});
