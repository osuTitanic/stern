function loadManifest() {
  var manifestUrl = '/api/clients/';
  var container = document.getElementById('client-container');

  console.info('Loading clients...');

  var xhr = new XMLHttpRequest();
  xhr.open('GET', manifestUrl, true);
  xhr.onreadystatechange = handleManifestResponse;
  xhr.send();

  function handleManifestResponse() {
      if (xhr.readyState !== 4) return;

      if (xhr.status === 200) {
          try {
              var manifest = JSON.parse(xhr.responseText);
              displayClients(manifest);
          } catch (e) {
              displayError('Failed to parse client data. Please contact an administrator!');
              console.error('Error parsing client manifest:', e);
          }
      } else {
          displayError('Failed to load clients. Please contact an administrator!');
          console.error('Error loading client manifest:', xhr.status);
      }
  }

  function displayClients(manifest) {
      for (var i = 0; i < manifest.length; i++) {
          var client = manifest[i];

          if (!client.supported || !client.recommended) continue;

          var clientDiv = createClientDiv(client);
          container.appendChild(clientDiv);
      }
  }

  function createClientDiv(client) {
      var div = document.createElement('div');
      div.style.maxWidth = client.screenshots[0].width + 'px';
      div.style.maxHeight = client.screenshots[0].height + 'px';
      div.className = 'client';

      if (client.known_bugs) {
          var bugsDiv = createBugsDiv(client.known_bugs);
          div.appendChild(bugsDiv);
      }

      div.appendChild(createTextElement('p', client.name, 'version'));
      div.appendChild(createTextElement('p', client.description, 'description'));
      div.appendChild(createImageElement(client.screenshots[0].src));
      div.appendChild(createDownloadLink(client.downloads[0]));

      return div;
  }

  function createBugsDiv(knownBugs) {
      var bugsDiv = document.createElement('div');
      bugsDiv.className = 'known-bugs';
      bugsDiv.title = knownBugs;

      var icon = document.createElement('i');
      icon.className = 'fa-solid fa-triangle-exclamation';
      icon.style.color = '#c40900';
      bugsDiv.appendChild(icon);

      return bugsDiv;
  }

  function createTextElement(tag, text, className) {
      var element = document.createElement(tag);
      element.textContent = text;
      element.className = className;
      return element;
  }

  function createImageElement(src) {
      var imgContainer = document.createElement('div');
      imgContainer.style.textAlign = 'center';
      var img = document.createElement('img');
      img.src = src;
      img.alt = 'Client Screenshot';
      imgContainer.appendChild(img);
      return imgContainer;
  }

  function createDownloadLink(href) {
      var link = document.createElement('a');
      link.className = 'download-link';
      link.target = '_blank';
      link.textContent = 'Download';
      link.href = href;
      return link;
  }

  function displayError(message) {
      var errorText = document.createElement('b');
      errorText.textContent = message;
      container.appendChild(errorText);
  }
}

window.addEventListener('load', loadManifest);
