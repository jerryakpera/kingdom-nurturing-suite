document.addEventListener('DOMContentLoaded', function () {
  // Get checkbox and textarea elements
  const movementCheckbox = document.getElementById(
    'is_movement_training_facilitator'
  );
  const movementTextarea = document.getElementById(
    'reason_is_not_movement_training_facilitator'
  );

  const skillCheckbox = document.getElementById(
    'is_skill_training_facilitator'
  );
  const skillTextarea = document.getElementById(
    'reason_is_not_skill_training_facilitator'
  );

  if (!movementCheckbox || !skillCheckbox) return;

  const mentorCheckbox = document.getElementById('is_mentor');
  const mentorTextarea = document.getElementById('reason_is_not_mentor');

  // Function to disable reason textarea based on checkbox state
  function toggleReasonTextarea(checkbox, textarea) {
    textarea.disabled = checkbox.checked;
    textarea.required = !checkbox.checked;
    textarea.value = ''; // Clear value when disabling
  }

  // Initial call to toggleReasonTextarea to set initial state
  toggleReasonTextarea(movementCheckbox, movementTextarea);
  toggleReasonTextarea(skillCheckbox, skillTextarea);
  toggleReasonTextarea(mentorCheckbox, mentorTextarea);

  // Add event listeners to checkboxes to toggle reason textareas
  movementCheckbox.addEventListener('change', function () {
    toggleReasonTextarea(movementCheckbox, movementTextarea);
  });
  skillCheckbox.addEventListener('change', function () {
    toggleReasonTextarea(skillCheckbox, skillTextarea);
  });
  mentorCheckbox.addEventListener('change', function () {
    toggleReasonTextarea(mentorCheckbox, mentorTextarea);
  });
});
