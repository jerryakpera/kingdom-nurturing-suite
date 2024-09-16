// document.addEventListener('DOMContentLoaded', () => {
//   const openButton = document.getElementById('open-consent-form-modal');
//   const closeButton = document.getElementById('close-consent-form-modal');

//   const $targetEl = document.getElementById('consent-form-modal');

//   const options = {
//     placement: 'top-left',
//     backdrop: 'dynamic',
//     backdropClasses: 'bg-gray-900/90 fixed inset-0 z-40',
//     closable: true,
//   };

//   const modal = new Modal($targetEl, options);

//   openButton.addEventListener('click', () => {
//     modal.show();
//   });

//   closeButton.addEventListener('click', () => {
//     modal.hide();
//   });
// });

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
