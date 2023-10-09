function loadManifest() {
    const manifestUrl = '/images/clients/manifest.json';
    const container = document.getElementById('client-container');
  
    console.info('Loading clients...');

    fetch(manifestUrl)
      .then(response => {
        if (!response.ok) {
          const errorText = document.createElement('b');
          errorText.textContent = 'Failed to load clients. Please contact an administrator!';
          container.appendChild(errorText);

          throw new Error(`Error: ${response.status}`);
        }
        return response.json();
      })
      .then(clients => {

        clients.forEach(client => {
            const version = document.createElement('p');
            version.textContent = client.version;
            version.classList.add('version')

            const description = document.createElement('p');
            description.textContent = client.description;
            description.classList.add('description')

            const screenshot = document.createElement('img');
            screenshot.style.height = client.height;
            screenshot.src = client.screenshot;

            const downloadLink = document.createElement('a');
            downloadLink.textContent = 'Download';
            downloadLink.href = client.download;
            downloadLink.setAttribute('target', '_blank');

            const div = document.createElement('div');
            div.style.maxWidth = client.width;
            div.classList.add('client');

            div.appendChild(version);
            div.appendChild(description);
            div.appendChild(screenshot);
            div.appendChild(downloadLink);

            container.appendChild(div);
        });
      })
      .catch(error => {
        console.error('Error loading client manifest:', error);
      });
}

window.addEventListener('load', loadManifest);