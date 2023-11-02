const Genres = {
    Any: 0,
    Unspecified: 1,
    Video_Game: 2,
    Anime: 3,
    Rock: 4,
    Pop: 5,
    Other: 6,
    Novelty: 7,
    HipHop: 9,
    Electronic: 10,
    Metal: 11,
    Classical: 12,
    Folk: 13,
    Jazz: 14,

    get: function(value) {return Object.keys(this).find(key => this[key] === value)}
};

const Languages = {
    Any: 0,
    Unspecified: 1,
    English: 2,
    Japanese: 3,
    Chinese: 4,
    Instrumental: 5,
    Korean: 6,
    French: 7,
    German: 8,
    Swedish: 9,
    Spanish: 10,
    Italian: 11,
    Russian: 12,
    Polish: 13,
    Other: 14,

    get: function(value) {return Object.keys(this).find(key => this[key] === value)}
};

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
                noMapsText.style.margin = "0 auto";
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

                var beatmapInfoLeft = document.createElement("div");
                beatmapInfoLeft.classList.add("beatmap-info-left");

                var beatmapLink = document.createElement("a");
                beatmapLink.classList.add("beatmap-link");
                beatmapLink.href = `/s/${beatmapset.id}`;
                beatmapLink.textContent = `${beatmapset.artist} - ${beatmapset.title}`;

                var videoIcon = document.createElement("i");
                videoIcon.classList.add("fa-solid", "fa-film");

                var imageIcon = document.createElement("i");
                imageIcon.classList.add("fa-regular", "fa-image");

                if (beatmapset.has_video)
                    beatmapInfoLeft.appendChild(videoIcon);

                if (beatmapset.has_storyboard)
                    beatmapInfoLeft.appendChild(imageIcon);

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

                beatmapInfoLeft.appendChild(beatmapLink);

                var beatmapInfoRight = document.createElement("div");
                beatmapInfoRight.classList.add("beatmap-info-right");

                var beatmapTagsDiv = document.createElement("div");
                beatmapTagsDiv.classList.add("beatmap-tags");

                if (beatmapset.language_id > 1)
                {
                    var query = new URLSearchParams(location.search);
                    query.set("language", beatmapset.language_id);
                    var languageTag = document.createElement("a");
                    languageTag.textContent = Languages.get(beatmapset.language_id).toString();
                    languageTag.href = `?${query.toString()}`
                    beatmapTagsDiv.appendChild(languageTag);
                }

                if (beatmapset.genre_id > 1)
                {
                    var query = new URLSearchParams(location.search);
                    query.set("genre", beatmapset.genre_id);
                    var genreTag = document.createElement("a");
                    genreTag.textContent = Genres.get(beatmapset.genre_id).toString().replace("_", " ");
                    genreTag.href = `?${query.toString()}`
                    beatmapTagsDiv.appendChild(genreTag);
                }

                beatmapInfoRight.appendChild(beatmapTagsDiv);
                beatmapsetDiv.appendChild(beatmapInfoLeft);
                beatmapsetDiv.appendChild(beatmapCreatorDiv);
                beatmapsetDiv.appendChild(beatmapInfoRight);
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