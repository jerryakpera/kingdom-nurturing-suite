document.addEventListener('DOMContentLoaded', () => {
  initModal(
    'open-filter-groups-modal-button',
    'close-filter-groups-modal-button',
    'filter-groups-modal',
    {
      placement: 'top-left',
      backdrop: 'static',
      backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
      closable: true,
    }
  );
});
