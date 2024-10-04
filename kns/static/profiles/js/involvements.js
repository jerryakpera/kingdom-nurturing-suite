document.addEventListener('DOMContentLoaded', function () {
  // Create an array of checkbox-textarea pairs
  const pairs = [
    {
      checkbox: document.getElementById('is_movement_training_facilitator'),
      textarea: document.getElementById(
        'reason_is_not_movement_training_facilitator'
      ),
    },
    {
      checkbox: document.getElementById('is_skill_training_facilitator'),
      textarea: document.getElementById(
        'reason_is_not_skill_training_facilitator'
      ),
    },
    {
      checkbox: document.getElementById('is_mentor'),
      textarea: document.getElementById('reason_is_not_mentor'),
    },
  ];

  // Function to disable reason textarea based on checkbox state
  function toggleReasonTextarea(checkbox, textarea) {
    textarea.disabled = checkbox.checked;
    textarea.required = !checkbox.checked;

    // Optional: Keep value when toggling
    // Comment out the next line if you want to retain textarea values when disabling
    textarea.value = checkbox.checked ? '' : textarea.value;

    // Apply a class to indicate the textarea is disabled
    textarea.classList.toggle('text-area-disabled', checkbox.checked);
  }

  // Loop through pairs to apply initial state and add event listeners
  pairs.forEach(({ checkbox, textarea }) => {
    if (checkbox && textarea) {
      toggleReasonTextarea(checkbox, textarea); // Initial state based on checkbox
      checkbox.addEventListener('change', () =>
        toggleReasonTextarea(checkbox, textarea)
      ); // Add listener
    }
  });
});
