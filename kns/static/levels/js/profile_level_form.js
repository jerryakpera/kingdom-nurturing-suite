document.addEventListener('DOMContentLoaded', async () => {
  const levelSelect = document.getElementById('level_select');

  await initializeSublevels(levelSelect.value);

  levelSelect.addEventListener('change', async (e) => {
    await initializeSublevels(e.target.value);
  });
});

async function initializeSublevels(levelId) {
  const urlInput = document.getElementById('url_input');
  const apiUrl = urlInput.dataset.url;

  try {
    const sublevels = await fetchSublevels(apiUrl, levelId);

    populateSublevelOptions(sublevels);
    toggleSublevelDisabled(sublevels.length);
  } catch (error) {
    console.error(error);
  }
}

async function fetchSublevels(apiUrl, levelId) {
  if (!levelId) return [];

  try {
    const response = await fetch(`${apiUrl}/levels/${levelId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch sublevels');
    }
    const { level } = await response.json();

    return level.sublevels;
  } catch (error) {
    throw new Error('Error fetching sublevels: ' + error.message);
  }
}

function toggleSublevelDisabled(sublevelsLength) {
  const sublevelSelect = document.getElementById('sublevel_select');

  sublevelSelect.removeAttribute('disabled');

  if (sublevelsLength === 0) {
    sublevelSelect.setAttribute('disabled', true);
  }
}

function createOption(id, title) {
  const option = document.createElement('option');

  option.value = id;
  option.text = title;

  return option;
}

function populateSublevelOptions(sublevels) {
  const sublevelSelect = document.getElementById('sublevel_select');

  // Clear previous options
  sublevelSelect.innerHTML = '';

  const defaultOption = createOption(null, '----------');
  sublevelSelect.appendChild(defaultOption);

  // Add new options for each sublevel
  sublevels.forEach((sublevel) => {
    const { id, title } = sublevel;
    const option = createOption(id, title);

    sublevelSelect.appendChild(option);
  });
}
