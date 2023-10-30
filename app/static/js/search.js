function getBeatmapsets()
{
    const beatmapContainer = document.getElementById("beatmap-list");
    const url = "/api/beatmapsets/search" + window.location.search

    fetch(url)
        .then(response => {
            if (!response.ok)
                throw new Error(`${response.status}`);
            return response.json();
        })
        .then(beatmapsets => {
            const loadingText = document.getElementById("loading-text");

            if (loadingText)
                loadingText.remove();

            if (beatmapsets.length <= 0)
            {
                var noMapsText = document.createElement("h3");
                noMapsText.textContent = "Nothing found... :("
                beatmapContainer.appendChild(noMapsText);
                return;
            }

            beatmapsets.forEach(beatmapset => {
                var beatmapsetDiv = document.createElement("div");
                beatmapsetDiv.classList.add("beatmapset");

                var beatmapImage = document.createElement("div");
                beatmapImage.classList.add("beatmap-image");
                beatmapImage.style.backgroundImage = `url("http://s.localhost/mt/${beatmapset.id}")`; // TODO: domain name...

                var playIcon = document.createElement("i");
                playIcon.classList.add("fa-solid", "fa-play");
                playIcon.id = `beatmap-preview-${beatmapset.id}`;

                beatmapImage.appendChild(playIcon);
                beatmapsetDiv.appendChild(beatmapImage);
                
                var beatmapInfo = document.createElement("div");
                beatmapInfo.classList.add("beatmap-info");

                var beatmapLink = document.createElement("a");
                beatmapLink.classList.add("beatmap-link");
                beatmapLink.href = `/s/${beatmapset.id}`;
                beatmapLink.textContent = `${beatmapset.artist} - ${beatmapset.title}`;

                var videoIcon = document.createElement("i");
                videoIcon.classList.add("fa-solid", "fa-film");

                var imageIcon = document.createElement("i");
                imageIcon.classList.add("fa-regular", "fa-image");

                if (beatmapset.has_video)
                    beatmapInfo.appendChild(videoIcon);

                if (beatmapset.has_storyboard)
                    beatmapInfo.appendChild(imageIcon);

                // TODO: More stuff lol

                beatmapInfo.appendChild(beatmapLink);
                beatmapsetDiv.appendChild(beatmapInfo);
                beatmapContainer.appendChild(beatmapsetDiv);
            });
        })
        .catch(error => {
            // TODO
            throw error;
        });
}

window.addEventListener('load', getBeatmapsets);