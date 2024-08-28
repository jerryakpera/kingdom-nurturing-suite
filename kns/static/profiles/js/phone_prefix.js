document.addEventListener('DOMContentLoaded', function () {
  const phoneField = document.getElementById('phone');
  const phonePrefixField = document.getElementById('phone_prefix');
  const locationCityField = document.getElementById('location_city');
  const locationCountryField = document.getElementById('location_country');

  // Load countries.json file
  fetch('/static/core/js/countries.json')
    .then((response) => response.json())
    .then((data) => {
      const countries = data;

      if (locationCountryField && phonePrefixField) {
        locationCountryField.addEventListener('change', function () {
          const countryCode = this.value;
          const phonePrefix = getPhonePrefix(countryCode, countries);
          phonePrefixField.value = phonePrefix;
        });
      }
    })
    .catch((error) => console.error('Error loading countries.json:', error));

  function getPhonePrefix(countryCode, countries) {
    // Find the country object in the countries array
    const country = countries.find((c) => c.iso === countryCode);
    return country ? country.code : '';
  }

  const countryCode = locationCountryField.value;
  toggleDisabledFields(countryCode);
  locationCountryField.addEventListener('change', function () {
    toggleDisabledFields(this.value);
  });

  function toggleDisabledFields(countryCode) {
    phoneField.disabled = Boolean(!countryCode);
    locationCityField.disabled = Boolean(!countryCode);
  }
});
