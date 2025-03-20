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

var currentPage = 0;
var totalBeatmaps = 0;
var busy = false;

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function getBeatmapIcon(beatmap) {
    var difficulty = "expert";

    if (beatmap.diff < 2.7) {
        difficulty = "easy";
    }
    else if (beatmap.diff < 3.7) {
        difficulty = "normal";
    }
    else if (beatmap.diff < 4.5) {
        difficulty = "hard";
    }
    else if (beatmap.diff < 5.5) {
        difficulty = "insane";
    }

    return "/images/beatmap/difficulties/" + difficulty + "-" + beatmap.mode + ".png";
}

function getSearchInput() {
    var dataElements = document.querySelectorAll(".beatmap-options dl");
    var json = {};

    for (var i = 0; i < dataElements.length; i++) {
        var item = dataElements[i];
        var dataName = item.getAttribute("data-name");

        if (!dataName) {
            var selectedElements = item.querySelectorAll(".selected");
            for (var j = 0; j < selectedElements.length; j++) {
                json[selectedElements[j].getAttribute("data-name")] = true;
            }
            continue;
        }

        var selectedElement = item.querySelector(".selected");
        var dataValue = selectedElement ? selectedElement.getAttribute("data-id") : "";

        if (dataValue.length > 0) {
            json[dataName] = dataValue;
        }
    }

    var orderSelection = document.querySelector(".beatmap-order-select img");
    var element = orderSelection.parentNode.querySelector("a");
    json["order"] = endsWith(orderSelection.src, "/images/down.gif") ? 0 : 1;
    json["sort"] = parseInt(element.getAttribute("data-id"));
    json["page"] = currentPage;

    var input = document.getElementById("search-input").value.trim();
    if (input.length > 0) {
        json["query"] = input;
    }

    return json;
}

function getBeatmapsets(clear) {    
    if (busy) {
        return;
    }
    
    if (clear) {
        // Clear current beatmaps
        var input = document.getElementById("beatmap-list");
        input.innerHTML = "";
        totalBeatmaps = 0;
        currentPage = 0;

        // Create loading text
        clearStatusText();
        var loadingText = document.createElement("h3");
        loadingText.textContent = "Loading...";
        loadingText.style.margin = "0 auto";
        loadingText.style.textAlign = "center";
        loadingText.id = "status-text";
        input.appendChild(loadingText);
    }

    if (totalBeatmaps > 0 && totalBeatmaps % 50 !== 0) {
        // No more beatmaps to load
        return;
    }

    var beatmapContainer = document.getElementById("beatmap-list");
    busy = true;

    performApiRequest("POST", "/beatmapsets/search", getSearchInput(), function(xhr) {
        var beatmapsets = JSON.parse(xhr.responseText);
        var loadingText = document.getElementById("status-text");

        if (loadingText) {
            loadingText.remove();
        }

        if (beatmapsets.length <= 0) {
            if (totalBeatmaps <= 0) {
                var noMapsText = document.createElement("h3");
                noMapsText.textContent = "Nothing found... :(";
                noMapsText.style.margin = "0 auto";
                noMapsText.style.textAlign = "center";
                beatmapContainer.appendChild(noMapsText);
            }
            busy = false;
            return;
        }

        beatmapsets.forEach(function(beatmapset) {
            var beatmapsetDiv = document.createElement("div");
            beatmapsetDiv.classList.add("beatmapset");

            var imageUrl = 'url("/mt/' + beatmapset.id + '")';

            // Use http for images if the page is not secure
            if (window.location.protocol != "https:") {
                imageUrl = imageUrl.replace("https://", "http://");
            }

            var beatmapImage = document.createElement("div");
            beatmapImage.classList.add("beatmap-image");
            beatmapImage.style.backgroundImage = imageUrl;

            var playIcon = document.createElement("i");
            playIcon.classList.add("fa-solid", "fa-play");
            playIcon.onclick = function(e) {
                var beatmapPreviewElements = document.querySelectorAll('[id^="beatmap-preview-"]');
                for (var i = 0; i < beatmapPreviewElements.length; i++) {
                    element = beatmapPreviewElements[i];

                    // Disable other active audios
                    if (!element.paused && element.id !== 'beatmap-preview-' + beatmapset.id) {
                        element.pause();
                        element.currentTime = 0;

                        var audioPlayIcon = element.parentElement.querySelector('.beatmap-image i');
                        audioPlayIcon.classList.remove("fa-pause");
                        audioPlayIcon.classList.add("fa-play");
                    }
                };

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
            beatmapAudio.src = '/mp3/preview/' + beatmapset.id;
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

            var beatmapArtist = document.createElement("span");
            beatmapArtist.textContent = beatmapset.artist;
            beatmapArtist.style.color = "#555555";

            var beatmapTitle = document.createElement("span");
            beatmapTitle.textContent = beatmapset.title;

            var beatmapLink = document.createElement("a");
            beatmapLink.classList.add("beatmap-link");
            beatmapLink.href = '/s/' + beatmapset.id;
            beatmapLink.appendChild(beatmapArtist);
            beatmapLink.appendChild(document.createTextNode(" - "));
            beatmapLink.appendChild(beatmapTitle);

            var beatmapInfoLeft = document.createElement("div");
            beatmapInfoLeft.classList.add("beatmap-info");

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

            var hiddenElementsContainer = document.createElement("div");
            hiddenElementsContainer.classList.add("hidden-elements");

            var beatmapSource = document.createElement("div");
            var beatmapSourceContent = document.createElement("span");
            beatmapSource.classList.add("beatmap-source");
            hiddenElementsContainer.appendChild(beatmapSource);

            if (beatmapset.source) {
                beatmapSourceContent.textContent = beatmapset.source;
                beatmapSource.appendChild(document.createTextNode("from "));
                beatmapSource.appendChild(beatmapSourceContent);
            }

            // Order beatmaps by difficulty and mode
            beatmapset.beatmaps.sort(function(a, b) {
                if (a.mode === b.mode) {
                    return a.diff - b.diff;
                }
                return a.mode - b.mode;
            });

            // Create icon for each beatmap inside set
            for (var i = 0; i < beatmapset.beatmaps.length; i++) {
                if (i >= 8) {
                    hiddenElementsContainer.appendChild(document.createTextNode("..."));
                    break;
                }

                var beatmap = beatmapset.beatmaps[i];
                var beatmapIconLink = document.createElement("a");
                var beatmapIcon = document.createElement("img");
                beatmapIcon.classList.add("beatmap-icon");
                beatmapIcon.src = getBeatmapIcon(beatmap);
                beatmapIcon.title = beatmap.version;
                beatmapIcon.alt = beatmap.version;
                beatmapIconLink.appendChild(beatmapIcon);
                beatmapIconLink.href = '/b/' + beatmap.id;
                hiddenElementsContainer.appendChild(beatmapIconLink);
            }

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
            beatmapsetDiv.appendChild(hiddenElementsContainer);
            beatmapContainer.appendChild(beatmapsetDiv);
        });

        $(".beatmapset").hover(
            function() {
                $(this).find(".beatmap-info").marquee({ speed: 50 });
                $(this).find(".hidden-elements").stop().fadeTo(1,100);
            },
            function() {
                $(this).find(".beatmap-info").attr('stop', 1);
                $(this).find(".hidden-elements").fadeOut(400);
            }
        );

        totalBeatmaps += beatmapsets.length;
        currentPage++;
        busy = false;
    }, function(xhr) {
        clearStatusText();
        var errorText = document.createElement("h3");
        errorText.textContent = "An error occurred while loading beatmaps.";
        errorText.style.margin = "0 auto";
        errorText.style.textAlign = "center";
        errorText.id = "status-text";

        beatmapContainer.appendChild(errorText);
        busy = false;
    });
}

function clearStatusText() {
    var loadingTexts = document.querySelectorAll("#status-text");

    for (var i = 0; i < loadingTexts.length; i++) {
        loadingTexts[i].remove();
    }
}

function setElement(element) {
    var dataName = element.parentNode.parentNode.getAttribute("data-name");
    var elements = element.parentNode.querySelectorAll("a");
    var removes = element.getAttribute("removes")

    if (removes) {
        var removeElement = document.querySelector('[data-name="' + removes + '"]');
        if (removeElement) {
            removeElement.classList.remove("selected");
        }
    }

    if (!dataName) {
        element.classList.toggle("selected");
        getBeatmapsets(true);
        return;
    }

    for (var i = 0; i < elements.length; i++) {
        if (elements[i] !== element) {
            elements[i].classList.remove("selected");
        }
    }

    element.classList.toggle("selected");

    if (!element.parentNode.querySelector(".selected")) {
        elements[0].classList.add("selected");
    }

    getBeatmapsets(true);
}

function setOrder(element) {
    var currentOrderSelection = document.querySelector(".beatmap-order-select img");
    var currentSortElement = currentOrderSelection.parentNode.querySelector("a");

    if (currentSortElement != element) {
        currentOrderSelection.remove();
    } else {
        currentOrderSelection.src = endsWith(currentOrderSelection.src, "/images/down.gif") ? "/images/up.gif" : "/images/down.gif";
        currentOrderSelection.alt = endsWith(currentOrderSelection.src, "/images/down.gif") ? "Descending" : "Ascending";
        getBeatmapsets(true);
        return;
    }

    var orderSelection = document.createElement("img");
    orderSelection.src = "/images/down.gif";
    orderSelection.alt = "Descending";
    element.parentElement.appendChild(orderSelection);
    getBeatmapsets(true);
}

var beatmapOptionsLinks = document.querySelectorAll(".beatmap-options a");
for (var i = 0; i < beatmapOptionsLinks.length; i++) {
    addEvent("click", beatmapOptionsLinks[i], function(event) {
        event.preventDefault();
        setElement(event.target);
    });
}

var beatmapOrderSelectLinks = document.querySelectorAll(".beatmap-order-select a");
for (var i = 0; i < beatmapOrderSelectLinks.length; i++) {
    addEvent("click", beatmapOrderSelectLinks[i], function(event) {
        event.preventDefault();
        setOrder(event.target);
    });
}

var input = document.getElementById("search-input");
var timeout = null;

addEvent('load', window, function(event) {
    getBeatmapsets(true);
});

addEvent("scroll", window, function(event) {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        getBeatmapsets(false);
    }
});

addEvent("keyup", input, function(event) {
    var input = document.getElementById("search-input");
    var query = [];
    var searchParams = location.search.substring(1).split("&");

    for (var i = 0; i < searchParams.length; i++) {
        var param = searchParams[i].split("=");
        if (param[0] !== "query") {
            query.push(param[0] + "=" + param[1]);
        }
    }

    clearTimeout(timeout);
    timeout = setTimeout(function() {
        getBeatmapsets(true);
    }, 500);
});