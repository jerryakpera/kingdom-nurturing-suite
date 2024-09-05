document.addEventListener('DOMContentLoaded', () => {
  const requestDrawerBtn = document.getElementById('requests-drawer-btn');

  const closeButtonId = 'close-requests-drawer-button';

  const $targetEl = document.getElementById('requests-drawer');

  const options = {
    closable: true,
    placement: 'right',
    backdrop: true,
    bodyScrolling: false,
    edge: false,
    edgeOffset: '',
    backdropClasses: 'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-30',
  };

  const drawer = new Drawer($targetEl, options);

  requestDrawerBtn.addEventListener('click', () => {
    drawer.show();
  });

  document.getElementById(closeButtonId).addEventListener('click', () => {
    drawer.hide();
  });
});
