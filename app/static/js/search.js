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

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            var beatmapsets = JSON.parse(xhr.responseText);
            var loadingText = document.getElementById("loading-text");

            if (loadingText) {
                loadingText.remove();
            }

            beatmapContainer.innerHTML = ""; // Remove child elements

            if (beatmapsets.length <= 0) {
                var noMapsText = document.createElement("h3");
                noMapsText.textContent = "Nothing found... :(";
                noMapsText.style.margin = "0 auto";
                noMapsText.style.textAlign = "center";
                beatmapContainer.appendChild(noMapsText);
                return;
            }

            beatmapsets.forEach(function(beatmapset) {
                var beatmapsetDiv = document.createElement("div");
                beatmapsetDiv.classList.add("beatmapset");

                var imageUrl = 'url("' + staticBaseurl + '/mt/' + beatmapset.id + '")';
                
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
        } else {
            console.error('Error loading beatmapsets: ' + xhr.statusText);
        }
    };

    xhr.onerror = function() {
        console.error('Network Error');
    };

    xhr.send();
}

function reloadInput() {
    var dataElements = document.querySelectorAll(".beatmap-options dl");
    var query = [];

    for (var i = 0; i < dataElements.length; i++) {
        var item = dataElements[i];
        var dataName = item.getAttribute("data-name");

        if (!dataName) {
            var selectedElements = item.querySelectorAll(".selected");
            for (var j = 0; j < selectedElements.length; j++) {
                query.push(selectedElements[j].getAttribute("data-name") + "=true");
            }
            continue;
        }

        var selectedElement = item.querySelector(".selected");
        var dataValue = selectedElement ? selectedElement.getAttribute("data-id") : "";

        if (dataValue.length > 0) {
            query.push(dataName + "=" + dataValue);
        }
    }

    // Keep search input from previous request
    var searchParams = new RegExp('[?&]query=([^&#]*)').exec(window.location.search);
    var search = searchParams ? searchParams[1] : null;
    if (search) query.push("query=" + search);

    // Keep sort from previous request
    var sortParams = new RegExp('[?&]sort=([^&#]*)').exec(window.location.search);
    var sort = sortParams ? sortParams[1] : null;
    if (sort) query.push("sort=" + sort);

    // Keep order from previous request
    var orderParams = new RegExp('[?&]order=([^&#]*)').exec(window.location.search);
    var order = orderParams ? orderParams[1] : null;
    if (order) query.push("order=" + order);

    location.search = "?" + query.join("&");
}

function setElement(element) {
    var dataName = element.parentNode.parentNode.getAttribute("data-name");
    var elements = element.parentNode.querySelectorAll("a");

    if (!dataName) {
        element.classList.toggle("selected");
        reloadInput();
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

    reloadInput();
}

function setOrder(element) {
    var query = [];
    var searchParams = location.search.substring(1).split("&");

    for (var i = 0; i < searchParams.length; i++) {
        var param = searchParams[i].split("=");
        if (param[0] !== "sort" && param[0] !== "page" && param[0] !== "order") {
            if (param[1] === undefined) {
                continue;
            }
            query.push(param[0] + "=" + param[1]);
        }
    }

    query.push("sort=" + element.getAttribute("data-id"));

    if (element.classList.contains("selected")) {
        var currentOrder = 0;
        for (var i = 0; i < searchParams.length; i++) {
            var param = searchParams[i].split("=");
            if (param[0] === "order") {
                currentOrder = parseInt(param[1]);
                break;
            }
        }
        query.push("order=" + (currentOrder == 0 ? 1 : 0));
    }

    location.search = "?" + query.join("&");
}

var beatmapOptionsLinks = document.querySelectorAll(".beatmap-options a");
for (var i = 0; i < beatmapOptionsLinks.length; i++) {
    beatmapOptionsLinks[i].addEventListener("click", function (event) {
        event.preventDefault();
        setElement(event.target);
    });
}

var beatmapOrderSelectLinks = document.querySelectorAll(".beatmap-order-select a");
for (var i = 0; i < beatmapOrderSelectLinks.length; i++) {
    beatmapOrderSelectLinks[i].addEventListener("click", function (event) {
        event.preventDefault();
        setOrder(event.target);
    });
}

window.addEventListener('load', function () {
    var dataElements = document.querySelectorAll(".beatmap-options dl");
    var searchParams = location.search.substring(1).split("&");
    var query = {};

    for (var i = 0; i < searchParams.length; i++) {
        var param = searchParams[i].split("=");
        query[param[0]] = param[1];
    }

    var beatmapOrder = query["order"] || 0;
    var beatmapSort = query["sort"] || 0;

    var orderElement = document.querySelector('.beatmap-order-select a[data-id="' + beatmapSort + '"]');
    if (orderElement) {
        orderElement.classList.add("selected");
    }

    for (var i = 0; i < dataElements.length; i++) {
        var item = dataElements[i];
        var dataName = item.getAttribute("data-name");

        if (!dataName) {
            var elements = item.querySelectorAll("a");
            for (var j = 0; j < elements.length; j++) {
                var element = elements[j];
                var elementDataName = element.getAttribute("data-name");
                if (elementDataName && query[elementDataName] === "true") {
                    element.classList.add("selected");
                }
            }
            continue;
        }

        var queryValue = query[dataName];
        if (queryValue) {
            var selectedItems = item.querySelectorAll(".selected");
            for (var j = 0; j < selectedItems.length; j++) {
                selectedItems[j].classList.remove("selected");
            }
            var selectedItem = item.querySelector('a[data-id="' + queryValue + '"]');
            if (selectedItem) {
                selectedItem.classList.add("selected");
            }
        }
    }

    getBeatmapsets();
});

var input = document.getElementById("search-input");
var timeout = null;

input.addEventListener("keyup", function (e) {
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
    timeout = setTimeout(function () {
        query.push("query=" + encodeURIComponent(input.value));
        location.search = "?" + query.join("&");
    }, 500);
});