document.addEventListener('DOMContentLoaded', async () => {
  const classificationSelect = document.getElementById('classification_select');

  await initializeSubclassifications(classificationSelect.value);

  classificationSelect.addEventListener('change', async (e) => {
    await initializeSubclassifications(e.target.value);
  });
});

async function initializeSubclassifications(classificationId) {
  const urlInput = document.getElementById('url_input');
  const apiUrl = urlInput.dataset.url;

  try {
    const subclassifications = await fetchSubclassifications(
      apiUrl,
      classificationId
    );

    populateSubclassificationOptions(subclassifications);
    toggleSubclassificationDisabled(subclassifications.length);
  } catch (error) {
    console.error(error);
  }
}

async function fetchSubclassifications(apiUrl, classificationId) {
  if (!classificationId) return [];

  try {
    const response = await fetch(
      `${apiUrl}/classifications/${classificationId}`
    );
    if (!response.ok) {
      throw new Error('Failed to fetch subclassifications');
    }
    const { classification } = await response.json();

    return classification.subclassifications;
  } catch (error) {
    throw new Error('Error fetching subclassifications: ' + error.message);
  }
}

function toggleSubclassificationDisabled(subclassificationsLength) {
  const subclassificationSelect = document.getElementById(
    'subclassification_select'
  );

  subclassificationSelect.removeAttribute('disabled');

  if (subclassificationsLength === 0) {
    subclassificationSelect.setAttribute('disabled', true);
  }
}

function createOption(id, title) {
  const option = document.createElement('option');

  option.value = id;
  option.text = title;

  return option;
}

function populateSubclassificationOptions(subclassifications) {
  const subclassificationSelect = document.getElementById(
    'subclassification_select'
  );

  // Clear previous options
  subclassificationSelect.innerHTML = '';

  const defaultOption = createOption(null, '----------');
  subclassificationSelect.appendChild(defaultOption);

  // Add new options for each subclassification
  subclassifications.forEach((subclassification) => {
    const { id, title } = subclassification;
    const option = createOption(id, title);

    subclassificationSelect.appendChild(option);
  });
}
