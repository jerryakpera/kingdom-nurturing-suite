document.addEventListener('DOMContentLoaded', function () {
  const startDateInput = document.getElementById('start_date');
  const registrationDeadlineDateInput = document.getElementById(
    'registration_deadline_date'
  );

  // Check if the elements exist
  if (!startDateInput) {
    return; // Stop executing the script if the element is not found
  }

  if (!registrationDeadlineDateInput) {
    return; // Stop executing the script if the element is not found
  }

  // Get the current date
  const today = new Date();
  // Get the date 3 days from today
  const minStartDate = new Date(today);
  minStartDate.setDate(minStartDate.getDate() + 3);

  // Format the date to YYYY-MM-DD for date input
  const formattedToday = formatDate(today);
  const formattedMinStartDate = formatDate(minStartDate);

  // Set the minimum date attribute for the start_date input
  startDateInput.setAttribute('min', formattedMinStartDate);

  // Set the minimum date attribute for the registration_deadline_date input
  registrationDeadlineDateInput.setAttribute('min', formattedToday);

  startDateInput.addEventListener('change', function () {
    handleStartDateChange(startDateInput.value);
  });

  // Check if startDateInput has a value
  if (startDateInput.value) {
    handleStartDateChange(startDateInput.value);
  }
});

function handleStartDateChange(startDateValue) {
  const minEndDate = getMinEndDate(startDateValue);
  const maxRegistrationDeadline = getMaxRegistrationDeadline(startDateValue);

  setDateFieldMinValue('end_date', minEndDate);
  setDateFieldMaxValue('registration_deadline_date', maxRegistrationDeadline);
}

function setDateFieldMinValue(fieldId, minDate) {
  const dateInput = document.getElementById(fieldId);

  dateInput.disabled = false;
  dateInput.setAttribute('min', minDate);
}

function setDateFieldMaxValue(fieldId, maxDate) {
  const dateInput = document.getElementById(fieldId);

  dateInput.disabled = false;
  dateInput.setAttribute('max', maxDate);
}

function getMinEndDate(date) {
  const selectedStartDate = new Date(date);
  selectedStartDate.setDate(selectedStartDate.getDate() + 1);
  const minEndDate = formatDate(selectedStartDate);

  return minEndDate;
}

function getMaxRegistrationDeadline(date) {
  const selectedStartDate = new Date(date);
  selectedStartDate.setDate(selectedStartDate.getDate() - 1);
  const maxRegistrationDeadline = formatDate(selectedStartDate);

  return maxRegistrationDeadline;
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = ('0' + (date.getMonth() + 1)).slice(-2);
  const day = ('0' + date.getDate()).slice(-2);
  const formattedDate = year + '-' + month + '-' + day;

  return formattedDate;
}
