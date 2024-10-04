document.addEventListener('DOMContentLoaded', function () {
  const textareas = document.querySelectorAll(
    'textarea[data-minlength][data-maxlength]'
  );

  textareas.forEach((textarea) => {
    const minLength = parseInt(textarea.getAttribute('data-minlength'), 10);
    const maxLength = parseInt(textarea.getAttribute('data-maxlength'), 10);

    const counter = document.createElement('div');

    counter.className = 'char-counter';

    counter.style.color = '#6b7280';
    counter.style.textAlign = 'right';
    counter.style.fontSize = '0.75rem';
    counter.style.fontWeight = 600;

    textarea.parentNode.insertBefore(counter, textarea.nextSibling);

    function updateCounter() {
      const length = textarea.value.length;

      counter.textContent = `${length}/${maxLength} characters`;

      if (length < minLength) {
        counter.style.color = '#ad343e';
      } else if (length > maxLength) {
        counter.style.color = '#ad343e';
      } else {
        counter.style.color = '#474747';
      }
    }

    // Initial update
    updateCounter();

    // Update on input
    textarea.addEventListener('input', updateCounter);
  });
});
