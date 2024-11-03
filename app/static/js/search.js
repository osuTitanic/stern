var Genres = {
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

    get: function(value) {
        var keys = Object.keys(this);
        for (var i = 0; i < keys.length; i++) {
            if (this[keys[i]] === value) {
                return keys[i];
            }
        }
        return undefined;
    }
};

var Languages = {
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

    get: function(value) {
        var keys = Object.keys(this);
        for (var i = 0; i < keys.length; i++) {
            if (this[keys[i]] === value) {
                return keys[i];
            }
        }
        return undefined;
    }
};

function getBeatmapsets() {
    var beatmapContainer = document.getElementById("beatmap-list");
    var url = "/api/beatmaps/search" + window.location.search;

    fetch(url)
        .then(function(response) {
            if (!response.ok) {
                throw new Error(response.status.toString());
            }
            return response.json();
        })
        .then(function(beatmapsets) {
            var loadingText = document.getElementById("loading-text");

            if (loadingText) {
                loadingText.remove();
            }

            beatmapContainer.innerHTML = ""; // Remove child elements

            if (beatmapsets.length <= 0) {
                var noMapsText = document.createElement("h3");
                noMapsText.textContent = "Nothing found... :(";
                noMapsText.style.margin = "0 auto";
                beatmapContainer.appendChild(noMapsText);
                return;
            }

            beatmapsets.forEach(function(beatmapset) {
                var beatmapsetDiv = document.createElement("div");
                beatmapsetDiv.classList.add("beatmapset");

                var beatmapImage = document.createElement("div");
                beatmapImage.classList.add("beatmap-image");
                beatmapImage.style.backgroundImage = 'url("' + staticBaseurl + '/mt/' + beatmapset.id + '")';

                var playIcon = document.createElement("i");
                playIcon.classList.add("fa-solid", "fa-play");
                playIcon.onclick = function(e) {
                    document.querySelectorAll('[id^="beatmap-preview-"]').forEach(function(element) {
                        // Disable other active audios
                        if (!element.paused && element.id !== 'beatmap-preview-' + beatmapset.id) {
                            element.pause();
                            element.currentTime = 0;

                            var audioPlayIcon = element.parentElement.querySelector('.beatmap-image i');
                            audioPlayIcon.classList.remove("fa-pause");
                            audioPlayIcon.classList.add("fa-play");
                        }
                    });

                    resetOrPlayAudio('beatmap-preview-' + beatmapset.id);

                    var audio = document.getElementById('beatmap-preview-' + beatmapset.id);

                    if (audio.paused) {
                        playIcon.classList.remove("fa-pause");
                        playIcon.classList.add("fa-play");
                    } else {
                        playIcon.classList.remove("fa-play");
                        playIcon.classList.add("fa-pause");
                    }
                };

                var beatmapAudio = document.createElement("audio");
                beatmapAudio.src = staticBaseurl + '/mp3/preview/' + beatmapset.id;
                beatmapAudio.id = 'beatmap-preview-' + beatmapset.id;
                beatmapAudio.volume = 0.5;
                beatmapAudio.onended = function() {
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
                beatmapLink.href = '/s/' + beatmapset.id;
                beatmapLink.textContent = beatmapset.artist + ' - ' + beatmapset.title;

                var videoIcon = document.createElement("i");
                videoIcon.classList.add("fa-solid", "fa-film");

                var imageIcon = document.createElement("i");
                imageIcon.classList.add("fa-regular", "fa-image");

                if (beatmapset.has_video) {
                    beatmapInfoLeft.appendChild(videoIcon);
                }

                if (beatmapset.has_storyboard) {
                    beatmapInfoLeft.appendChild(imageIcon);
                }

                var beatmapCreator = document.createElement("span");
                beatmapCreator.textContent = "mapped by ";

                var beatmapCreatorLink = document.createElement("a");
                beatmapCreatorLink.textContent = beatmapset.creator;
                if (beatmapset.server === 0) {
                    beatmapCreatorLink.href = 'https://osu.ppy.sh/u/' + beatmapset.creator;
                } else {
                    beatmapCreatorLink.href = '/u/' + beatmapset.creator_id;
                }

                var beatmapCreatorDiv = document.createElement("div");
                beatmapCreatorDiv.appendChild(beatmapCreator);
                beatmapCreatorDiv.appendChild(beatmapCreatorLink);
                beatmapCreatorDiv.classList.add("beatmap-creator");

                beatmapInfoLeft.appendChild(beatmapLink);

                var beatmapInfoRight = document.createElement("div");
                beatmapInfoRight.classList.add("beatmap-stats");

                var beatmapTagsDiv = document.createElement("div");
                beatmapTagsDiv.classList.add("beatmap-tags");

                if (beatmapset.language_id > 0) {
                    var query = new URLSearchParams(location.search);
                    query.set("language", beatmapset.language_id);
                    var languageTag = document.createElement("a");
                    languageTag.textContent = Languages.get(beatmapset.language_id).toString();
                    languageTag.href = '?' + query.toString();
                    beatmapTagsDiv.appendChild(languageTag);
                }

                if (beatmapset.genre_id > 0) {
                    var query = new URLSearchParams(location.search);
                    query.set("genre", beatmapset.genre_id);
                    var genreTag = document.createElement("a");
                    genreTag.textContent = Genres.get(beatmapset.genre_id).toString().replace("_", " ");
                    genreTag.href = '?' + query.toString();
                    beatmapTagsDiv.appendChild(genreTag);
                }

                var ratingBar = document.createElement("div");
                ratingBar.style.width = (100 - ((beatmapset.ratings / 10) * 100)) + '%';
                ratingBar.classList.add("beatmap-rating-bar");

                var beatmapRating = document.createElement("div");
                beatmapRating.classList.add("beatmap-rating");
                beatmapRating.appendChild(ratingBar);

                var heartIcon = document.createElement("i");
                heartIcon.classList.add("fa-solid", "fa-heart");

                var playsIcon = document.createElement("i");
                playsIcon.classList.add("fa-solid", "fa-play");

                var totalPlays = beatmapset.beatmaps
                    .map(function(item) {
                        return item.playcount;
                    })
                    .reduce(function(prev, next) {
                        return prev + next;
                    });

                var detailsDiv = document.createElement("div");
                detailsDiv.classList.add("beatmap-details");
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
        .catch(function(error) {
            // TODO
            throw error;
        });
}

function reloadInput() {
    var dataElements = document.querySelectorAll(".beatmap-options dl");
    var query = new URLSearchParams();

    dataElements.forEach(function(item) {
        var dataName = item.getAttribute("data-name");

        // Element has no "data-name"
        // Multiple selections can be made
        if (!dataName) {
            item.querySelectorAll(".selected").forEach(function(selectedItem) {
                query.append("mods[]", selectedItem.getAttribute("data-id"));
            });
        } else {
            var selectedElement = item.querySelector(".selected");
            if (selectedElement) {
                query.set(dataName, selectedElement.getAttribute("data-id"));
            }
        }
    });

    var searchParams = window.location.search ? window.location.search + '&' : '?';
    searchParams += query.toString();

    history.pushState(null, '', searchParams);
    getBeatmapsets();
}

// Get beatmapsets on load
getBeatmapsets();