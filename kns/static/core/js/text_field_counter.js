document.addEventListener('DOMContentLoaded', function () {
  const inputsAndTextareas = document.querySelectorAll(
    'textarea[data-minlength][data-maxlength], input[type="text"][data-minlength][data-maxlength]'
  );

  inputsAndTextareas.forEach((input) => {
    const minLength = parseInt(input.getAttribute('data-minlength'), 10);
    const maxLength = parseInt(input.getAttribute('data-maxlength'), 10);

    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.style.color = '#6b7280';
    counter.style.textAlign = 'right';
    counter.style.fontSize = '0.75rem';
    counter.style.fontWeight = 600;

    input.parentNode.insertBefore(counter, input.nextSibling);

    function updateCounter() {
      const length = input.value.length;
      counter.textContent = `${length}/${maxLength} characters`;

      if (length < minLength || length > maxLength) {
        counter.style.color = '#ad343e'; // Error color
      } else {
        counter.style.color = '#474747'; // Normal color
      }
    }

    function toggleCounterVisibility() {
      if (input.disabled) {
        counter.style.display = 'none'; // Hide if disabled
      } else {
        counter.style.display = 'block'; // Show if enabled
        updateCounter(); // Update counter when it's re-enabled
      }
    }

    // Initial update and visibility check
    updateCounter();
    toggleCounterVisibility();

    // Update on input (works for both textareas and text inputs)
    input.addEventListener('input', updateCounter);

    // Listen for changes to the disabled state (you can toggle disabled state externally)
    const observer = new MutationObserver(function () {
      toggleCounterVisibility();
    });

    observer.observe(input, {
      attributes: true,
      attributeFilter: ['disabled'],
    });
  });
});
