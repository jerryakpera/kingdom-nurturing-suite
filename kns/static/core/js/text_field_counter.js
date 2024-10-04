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

      if (length < minLength || length > maxLength) {
        counter.style.color = '#ad343e'; // Error color
      } else {
        counter.style.color = '#474747'; // Normal color
      }
    }

    function toggleCounterVisibility() {
      if (textarea.disabled) {
        counter.style.display = 'none'; // Hide if disabled
      } else {
        counter.style.display = 'block'; // Show if enabled
        updateCounter(); // Update counter when it's re-enabled
      }
    }

    // Initial update and visibility check
    updateCounter();
    toggleCounterVisibility();

    // Update on input
    textarea.addEventListener('input', updateCounter);

    // Listen for changes to the disabled state (you can toggle disabled state externally)
    const observer = new MutationObserver(function () {
      toggleCounterVisibility();
    });

    observer.observe(textarea, {
      attributes: true,
      attributeFilter: ['disabled'],
    });
  });
});
