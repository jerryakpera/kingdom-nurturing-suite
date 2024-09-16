document.addEventListener('DOMContentLoaded', () => {
  initModal(
    'open-consent-form-read-more-modal',
    'close-consent-form-read-more-modal',
    'consent-formread-more-modal',
    {
      placement: 'top-left',
      backdrop: 'static',
      closable: true,
    }
  );
});
