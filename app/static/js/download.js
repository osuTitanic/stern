function loadManifest()
{
  // Clients will be dynamically loaded from manifest.json
  const manifestUrl = '/clients/manifest.json';
  const container = document.getElementById('client-container');

  console.info('Loading clients...');

  fetch(manifestUrl)
    .then(response => {
      if (!response.ok) {
        // Let user know that something went wrong
        const errorText = document.createElement('b');
        errorText.textContent = 'Failed to load clients. Please contact an administrator!';
        container.appendChild(errorText);
        throw new Error(`Error: ${response.status}`);
      }
      return response.json();
    })
    .then(manifest => {
      // Create client div's for each entry in manifest
      manifest['downloads'].forEach(client => {
          const version = document.createElement('p');
          version.textContent = client.version;
          version.classList.add('version')

          const description = document.createElement('p');
          description.textContent = client.description;
          description.classList.add('description')

          const screenshot = document.createElement('img');
          screenshot.src = client.screenshot;

          const downloadLink = document.createElement('a');
          downloadLink.setAttribute('target', '_blank');
          downloadLink.textContent = 'Download';
          downloadLink.href = client.download;

          const div = document.createElement('div');
          div.style.maxWidth = client.maxWidth;
          div.classList.add('client');

          div.appendChild(version);
          div.appendChild(description);
          div.appendChild(screenshot);
          div.appendChild(downloadLink);

          container.appendChild(div);
      });
    })
    .catch(error => {
      const errorText = document.createElement('b');
      errorText.textContent = 'Failed to load clients. Please contact an administrator!';
      container.appendChild(errorText);
      console.error('Error loading client manifest:', error);
    });
}

window.addEventListener('load', loadManifest);