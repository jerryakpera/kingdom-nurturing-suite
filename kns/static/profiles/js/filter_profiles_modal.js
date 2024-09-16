document.addEventListener('DOMContentLoaded', () => {
  initModal(
    'open-filter-profiles-modal-button',
    'close-filter-profiles-modal-button',
    'filter-profiles-modal',
    {
      placement: 'top-left',
      backdrop: 'static',
      backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
      closable: true,
    }
  );
});
