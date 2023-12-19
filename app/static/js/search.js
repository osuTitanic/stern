const Genres = {
    Any: 0,
    Unspecified: 1,
    Video_Game: 2,
    Anime: 3,
    Rock: 4,
    Pop: 5,
    Other: 6,
    Novelty: 7,
    Hip_Hop: 9,
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
                beatmapImage.style.backgroundImage = `url("http${enableSSL ? 's' : ''}://s.${domainName}/mt/${beatmapset.id}")`;

                var playIcon = document.createElement("i");
                playIcon.classList.add("fa-solid", "fa-play");
                playIcon.onclick = (e) => {
                    document.querySelectorAll('[id^="beatmap-preview-"]').forEach(element => {
                        // Disable other active audios
                        if (!element.paused && element.id != `beatmap-preview-${beatmapset.id}`)
                        {
                            element.pause();
                            element.currentTime = 0;

                            var audioPlayIcon = element.parentElement.querySelector('.beatmap-image i');
                            audioPlayIcon.classList.remove("fa-pause");
                            audioPlayIcon.classList.add("fa-play");
                        }
                    });

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
                beatmapAudio.src = `http${enableSSL ? 's' : ''}://s.${domainName}/mp3/preview/${beatmapset.id}`;
                beatmapAudio.id = `beatmap-preview-${beatmapset.id}`;
                beatmapAudio.onended = () => {
                    playIcon.classList.remove("fa-pause");
                    playIcon.classList.add("fa-play");
                };

                beatmapImage.appendChild(playIcon);
                beatmapsetDiv.appendChild(beatmapImage);
                beatmapsetDiv.appendChild(beatmapAudio);

                var beatmapInfoLeft = document.createElement("div");
                beatmapInfoLeft.classList.add("beatmap-info");

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
                beatmapInfoRight.classList.add("beatmap-stats");

                var beatmapTagsDiv = document.createElement("div");
                beatmapTagsDiv.classList.add("beatmap-tags");

                if (beatmapset.language_id > 0)
                {
                    var query = new URLSearchParams(location.search);
                    query.set("language", beatmapset.language_id);
                    var languageTag = document.createElement("a");
                    languageTag.textContent = Languages.get(beatmapset.language_id).toString();
                    languageTag.href = `?${query.toString()}`
                    beatmapTagsDiv.appendChild(languageTag);
                }

                if (beatmapset.genre_id > 0)
                {
                    var query = new URLSearchParams(location.search);
                    query.set("genre", beatmapset.genre_id);
                    var genreTag = document.createElement("a");
                    genreTag.textContent = Genres.get(beatmapset.genre_id).toString().replace("_", " ");
                    genreTag.href = `?${query.toString()}`
                    beatmapTagsDiv.appendChild(genreTag);
                }

                var ratingBar = document.createElement("div");
                ratingBar.style.width = `${100 - ((beatmapset.ratings / 10) * 100)}%`;
                ratingBar.classList.add("beatmap-rating-bar");

                var beatmapRating = document.createElement("div");
                beatmapRating.classList.add("beatmap-rating");
                beatmapRating.appendChild(ratingBar);

                var heartIcon = document.createElement("i");
                heartIcon.classList.add("fa-solid", "fa-heart");

                var playsIcon = document.createElement("i");
                playsIcon.classList.add("fa-solid", "fa-play");

                var totalPlays = beatmapset.beatmaps
                            .map((item) => item.playcount)
                            .reduce((prev, next) => prev + next);

                var detailsDiv = document.createElement("div");
                detailsDiv.classList.add("beatmap-details")
                detailsDiv.appendChild(heartIcon);
                detailsDiv.appendChild(document.createTextNode(beatmapset.favourites));
                detailsDiv.appendChild(playsIcon);
                detailsDiv.appendChild(document.createTextNode(totalPlays));

                beatmapInfoRight.appendChild(beatmapTagsDiv);
                beatmapInfoRight.appendChild(beatmapRating);
                beatmapInfoRight.appendChild(detailsDiv);

                beatmapsetDiv.appendChild(beatmapInfoLeft);
                beatmapsetDiv.appendChild(beatmapCreatorDiv);
                beatmapsetDiv.appendChild(beatmapInfoRight);
                beatmapContainer.appendChild(beatmapsetDiv);

                $(".pagination").css("display", "block");
            });
        })
        .catch(error => {
            // TODO
            throw error;
        });
}

function reloadInput()
{
    const dataElements = document.querySelectorAll(".beatmap-options dl");
    var query = new URLSearchParams();

    dataElements.forEach(item => {
        var dataName = item.getAttribute("data-name");

        // Element has no "data-name"
        // Multiple selections can be made
        if (!dataName)
        {
            item.querySelectorAll(".selected")
                .forEach(selectedElement => {
                    query.set(selectedElement.getAttribute("data-name"), "true");
                });
            return;
        }

        var selectedElement = item.querySelector(".selected");
        var dataValue = selectedElement.getAttribute("data-id");

        // Don't set parameter if "data-id" is empty
        if (dataValue.length > 0)
            query.set(dataName, dataValue);
    });

    // Keep search input from previous request
    var search = new URLSearchParams(location.search).get("query");
    if (search) query.set("query", search);

    // Browser will reload
    location.search = query.toString();
}

function setElement(element)
{
    const dataName = element.parentNode.parentNode.getAttribute("data-name");
    const elements = element.parentNode.querySelectorAll("a");

    if (!dataName)
    {
        element.classList.toggle("selected");
        reloadInput();
        return;
    }

    elements.forEach(dataElement => {
        if (dataElement !== element)
            dataElement.classList.remove("selected");
    });

    element.classList.toggle("selected");

    // Select default/first element if no element was selected
    if (!element.parentNode.querySelector(".selected"))
        elements[0].classList.add("selected");

    reloadInput();
}

function setOrder(element)
{
    const query = new URLSearchParams(location.search);
    query.set("sort", element.getAttribute("data-id"));
    query.delete("page");

    if (element.classList.contains("selected"))
    {
        // 0 - Descending
        // 1 - Ascending
        const currentOrder = query.get("order") || 0;
        query.set("order", (currentOrder == 0 ? 1 : 0));
    }

    // Browser will reload
    location.search = query.toString();
}

document.querySelectorAll(".beatmap-options a")
        .forEach(selectableElement => {
            selectableElement.addEventListener("click", (event) => {
                event.preventDefault();
                setElement(event.target);
            })
        });

document.querySelectorAll(".beatmap-order-select a")
        .forEach(selectableElement => {
            selectableElement.addEventListener("click", (event) => {
                event.preventDefault();
                setOrder(event.target);
            })
        });

window.addEventListener('load', () => {
    const dataElements = document.querySelectorAll(".beatmap-options dl");
    const query = new URLSearchParams(location.search);

    const beatmapOrder = query.get("order") || 0;
    const beatmapSort = query.get("sort") || 0;

    const orderElement = document.querySelector(`.beatmap-order-select a[data-id="${beatmapSort}"]`);
    orderElement.classList.add("selected");

    // Reset "selected" class based on query
    dataElements.forEach(item => {
        var dataName = item.getAttribute("data-name");

        if (!dataName)
        {
            // Element has no "data-name"
            // Multiple selections can be made
            item.querySelectorAll("a").forEach(element => {
                const elementDataName = element.getAttribute("data-name");

                if (elementDataName) {
                    const queryValue = query.get(elementDataName);
                    element.classList.toggle("selected", queryValue === "true");
                }
            })
            return;
        }

        const queryValue = query.get(dataName);

        if (queryValue)
        {
            item.querySelectorAll(".selected").forEach(selectedElement => {
                selectedElement.classList.remove("selected");
            });

            const selectedItem = item.querySelector(`a[data-id="${queryValue}"]`);
            if (selectedItem) {
                selectedItem.classList.add("selected");
            }
        }
    });

    // Load beatmapsets
    getBeatmapsets();
});

var input = document.getElementById("search-input");
var timeout = null;

// Event listener for search query input
input.addEventListener("keyup", (e) => {
    var input = document.getElementById("search-input");
    var query = new URLSearchParams(location.search);

    clearTimeout(timeout);

    timeout = setTimeout(() => {
        query.set("query", input.value);
        location.search = query.toString();
    }, 500);
});