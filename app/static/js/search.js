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

            beatmapContainer.innerHTML = ""; // Remove child elements

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
                beatmapImage.style.backgroundImage = `url("http://s.${domainName}/mt/${beatmapset.id}")`;

                var playIcon = document.createElement("i");
                playIcon.classList.add("fa-solid", "fa-play");
                playIcon.onclick = (e) => {
                    resetOrPlayAudio(`beatmap-preview-${beatmapset.id}`);

                    var audio = document.getElementById(`beatmap-preview-${beatmapset.id}`);

                    if (audio.paused)
                    {
                        playIcon.classList.remove("fa-pause");
                        playIcon.classList.add("fa-play");
                    }
                    else
                    {
                        playIcon.classList.remove("fa-play");
                        playIcon.classList.add("fa-pause");
                    }
                };

                var beatmapAudio = document.createElement("audio");
                beatmapAudio.src = `http://s.${domainName}/mp3/preview/${beatmapset.id}`;
                beatmapAudio.id = `beatmap-preview-${beatmapset.id}`;
                beatmapAudio.onended = () => {
                    playIcon.classList.remove("fa-pause");
                    playIcon.classList.add("fa-play");
                };

                beatmapImage.appendChild(playIcon);
                beatmapsetDiv.appendChild(beatmapImage);
                beatmapsetDiv.appendChild(beatmapAudio);

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

                beatmapCreator = document.createElement("span");
                beatmapCreator.textContent = "mapped by ";

                beatmapCreatorLink = document.createElement("a");
                beatmapCreatorLink.textContent = beatmapset.creator;
                if (beatmapset.server == 0) beatmapCreatorLink.href = `https://osu.ppy.sh/u/${beatmapset.creator}`
                else beatmapCreatorLink.href = `/u/${set.creator}` // TODO: CreatorId

                beatmapCreatorDiv = document.createElement("div");
                beatmapCreatorDiv.appendChild(beatmapCreator);
                beatmapCreatorDiv.appendChild(beatmapCreatorLink);
                beatmapCreatorDiv.classList.add("beatmap-creator");

                beatmapInfo.appendChild(beatmapLink);
                beatmapInfo.appendChild(beatmapCreatorDiv);
                beatmapsetDiv.appendChild(beatmapInfo);
                beatmapContainer.appendChild(beatmapsetDiv);
            });
        })
        .catch(error => {
            // TODO
            throw error;
        });
}

function reloadInput()
{
    var query = new URLSearchParams(location.search);
    var category = document.getElementById("category").value;
    var mode = document.getElementById("mode").value;

    var storyboard = document.getElementById("storyboard").checked;
    var video = document.getElementById("video").checked;

    query.delete("category");
    query.delete("mode");
    query.delete("storyboard");
    query.delete("video");

    if (category != 1) query.set("category", category);
    if (mode != -1) query.set("mode", mode);

    if (storyboard == true) query.set("storyboard", true);
    if (video == true) query.set("video", true);

    // Browser will reload
    location.search = query.toString();
}

function setInput()
{
    var query = new URLSearchParams(location.search);

    var storyboard = document.getElementById("storyboard");
    var video = document.getElementById("video");

    if (query.get("storyboard")) storyboard.checked = true;
    if (query.get("video")) video.checked = true;

    var category = document.getElementById("category");
    var mode = document.getElementById("mode");

    if (query.get("category")) category.value = query.get("category");
    if (query.get("mode")) mode.value = query.get("mode");

    getBeatmapsets();
}

var input = document.getElementById("search-input");
var timeout = null;

input.addEventListener("keyup", (e) => {
    var input = document.getElementById("search-input");
    var query = new URLSearchParams(location.search);

    clearTimeout(timeout);

    timeout = setTimeout(() => {
        query.set("query", input.value);
        location.search = query.toString();
    }, 500);
});

window.addEventListener('load', setInput);