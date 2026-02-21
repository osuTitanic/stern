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
        var keys = getObjectKeys(this);
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
        var keys = getObjectKeys(this);
        for (var i = 0; i < keys.length; i++) {
            if (this[keys[i]] === value) {
                return keys[i];
            }
        }
        return undefined;
    }
};

var totalBeatmaps = 0;
var currentPage = 0;
var busy = false;

function getBeatmapIcon(beatmap) {
    var difficulty = "expert";

    if (beatmap.diff < 2) {
        difficulty = "easy";
    }
    else if (beatmap.diff < 2.7) {
        difficulty = "normal";
    }
    else if (beatmap.diff < 4) {
        difficulty = "hard";
    }
    else if (beatmap.diff < 5.3) {
        difficulty = "insane";
    }

    return "/images/beatmap/difficulties/" + difficulty + "-" + beatmap.mode + ".png";
}

function getSearchInput() {
    if (document.querySelectorAll === undefined) {
        // lets not even attempt this
        return {};
    }

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

    var input = trimString(document.getElementById("search-input").value);
    if (input.length > 0) {
        json["query"] = input;
    }

    return json;
}

function getPageParameter() {
    try {
        var searchParams = new URLSearchParams(window.location.search);
        var pageParam = parseInt(searchParams.get("page"));
    } catch (e) {
        console.error(e);
        var pageParam = 0;
    }

    if (isNaN(pageParam) || pageParam < 0) {
        pageParam = 0;
    }

    return pageParam;
}

function getBeatmapsets(clear) {    
    if (busy) {
        return;
    }
    
    if (clear) {
        // Clear current beatmaps
        var input = document.getElementById("beatmap-list");
        input.innerHTML = "";

        currentPage = getPageParameter();
        totalBeatmaps = 0;

        // Create loading text
        clearStatusText();
        var loadingText = document.createElement("h3");
        setText(loadingText, "Loading...");
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
            loadingText.parentNode.removeChild(loadingText);
        }

        if (beatmapsets.length <= 0) {
            if (totalBeatmaps <= 0) {
                var noMapsText = document.createElement("h3");
                setText(noMapsText, "Nothing found... :(");
                noMapsText.style.margin = "0 auto";
                noMapsText.style.textAlign = "center";
                beatmapContainer.appendChild(noMapsText);
            }
            busy = false;
            return;
        }

        for (var beatmapsetIndex = 0; beatmapsetIndex < beatmapsets.length; beatmapsetIndex++) {
            var beatmapset = beatmapsets[beatmapsetIndex];
            var beatmapsetDiv = document.createElement("div");
            addClass(beatmapsetDiv, "beatmapset");
            beatmapsetDiv.id = "beatmapset-" + beatmapset.id;

            var lastUpdate = beatmapset.last_update;
            var lastUpdateTimestamp = Math.floor(Date.parse(lastUpdate) / 1000);

            var imageUrl = 'url("/mt/' + beatmapset.id + '?c=' + lastUpdateTimestamp + '")';

            // Use http for images if the page is not secure
            if (window.location.protocol != "https:") {
                imageUrl = imageUrl.replace("https://", "http://");
            }

            var beatmapImage = document.createElement("div");
            addClass(beatmapImage, "beatmap-image");
            beatmapImage.style.backgroundImage = imageUrl;

            var beatmapSideOptions = document.createElement("div");
            addClass(beatmapSideOptions, "beatmap-side-options");
            beatmapSideOptions.style.display = "none";
            beatmapSideOptions.style.overflow = "hidden";
            beatmapSideOptions.style.width = "24px";

            var heartIcon = document.createElement("i");
            addClasses(heartIcon, ["icon-heart"]);
            var favouriteLink = document.createElement("a");
            favouriteLink.href = "#";
            favouriteLink.appendChild(heartIcon);
            beatmapSideOptions.appendChild(favouriteLink);

            var speechBubbleIcon = document.createElement("i");
            addClasses(speechBubbleIcon, ["icon-comment"]);
            var commentsLink = document.createElement("a");
            commentsLink.href = '/forum/t/' + beatmapset.topic_id;
            commentsLink.appendChild(speechBubbleIcon);
            beatmapSideOptions.appendChild(commentsLink);

            var downloadIcon = document.createElement("i");
            addClasses(downloadIcon, ["icon-download-alt"]);
            var downloadLink = document.createElement("a");
            downloadLink.href = '/d/' + beatmapset.id;
            downloadLink.appendChild(downloadIcon);
            beatmapSideOptions.appendChild(downloadLink);

            if (beatmapset.server == 0) {
                commentsLink.href = 'https://osu.ppy.sh/beatmapsets/' + beatmapset.id + '#comments';
            }

            if (!currentUser) {
                favouriteLink.onclick = function(e) {
                    preventEventDefault(e || window.event);
                    showLoginForm();
                }
                downloadLink.onclick = function(e) {
                    preventEventDefault(e || window.event);
                    showLoginForm();
                }
            } else {
                favouriteLink.onclick = function(e) {
                    preventEventDefault(e || window.event);
                    addFavorite(beatmapset.id);
                }
            }

            var playIcon = document.createElement("i");
            addClasses(playIcon, ["icon-play"]);
            playIcon.onclick = function(e) {
                var beatmapPreviewElements = document.querySelectorAll('[id^="beatmap-preview-"]');
                for (var i = 0; i < beatmapPreviewElements.length; i++) {
                    element = beatmapPreviewElements[i];

                    // Disable other active audios
                    if (!element.paused && element.id !== 'beatmap-preview-' + beatmapset.id) {
                        element.pause();
                        element.currentTime = 0;

                        var audioPlayIcon = getParentElement(element).querySelector('.beatmap-image i');
                        removeClass(audioPlayIcon, "icon-pause");
                        addClass(audioPlayIcon, "icon-play");
                    }
                };

                resetOrPlayAudio('beatmap-preview-' + beatmapset.id);
                var audio = document.getElementById('beatmap-preview-' + beatmapset.id);

                if (audio.paused) {
                    removeClass(playIcon, "icon-pause");
                    addClass(playIcon, "icon-play");
                } else {
                    removeClass(playIcon, "icon-play");
                    addClass(playIcon, "icon-pause");
                }
            };

            var lastUpdate = beatmapset.last_update;
            var lastUpdateTimestamp = Math.floor(Date.parse(lastUpdate) / 1000);

            var beatmapAudio = document.createElement("audio");
            beatmapAudio.src = '/mp3/preview/' + beatmapset.id + '?c=' + lastUpdateTimestamp;
            beatmapAudio.id = 'beatmap-preview-' + beatmapset.id;
            beatmapAudio.volume = 0.5;
            beatmapAudio.onended = function() {
                removeClass(playIcon, "icon-pause");
                addClass(playIcon, "icon-play");
            };

            beatmapImage.appendChild(playIcon);
            beatmapsetDiv.appendChild(beatmapImage);
            beatmapsetDiv.appendChild(beatmapAudio);
            beatmapsetDiv.appendChild(beatmapSideOptions);

            var beatmapInfoLeft = document.createElement("div");
            addClass(beatmapInfoLeft, "beatmap-info");

            var beatmapArtist = document.createElement("span");
            setText(beatmapArtist, beatmapset.artist);
            beatmapArtist.style.color = "#555555";

            var beatmapTitle = document.createElement("span");
            addClass(beatmapTitle, "beatmap-title");
            setText(beatmapTitle, beatmapset.title);

            var beatmapLink = document.createElement("a");
            addClass(beatmapLink, "beatmap-link");
            beatmapLink.href = '/s/' + beatmapset.id;
            beatmapLink.appendChild(beatmapArtist);
            beatmapLink.appendChild(document.createTextNode(" - "));
            beatmapLink.appendChild(beatmapTitle);

            var beatmapInfoLeft = document.createElement("div");
            addClass(beatmapInfoLeft, "beatmap-info");

            var videoIcon = document.createElement("i");
            addClasses(videoIcon, ["icon-film"]);

            var imageIcon = document.createElement("i");
            addClasses(imageIcon, ["icon-image"]);

            if (beatmapset.has_video) {
                beatmapInfoLeft.appendChild(videoIcon);
            }

            if (beatmapset.has_storyboard) {
                beatmapInfoLeft.appendChild(imageIcon);
            }

            var beatmapCreator = document.createElement("span");
            setText(beatmapCreator, "mapped by ");

            var beatmapCreatorLink = document.createElement("a");
            setText(beatmapCreatorLink, beatmapset.creator);
            if (beatmapset.server === 0) {
                beatmapCreatorLink.href = 'https://osu.ppy.sh/u/' + beatmapset.creator;
            } else {
                beatmapCreatorLink.href = '/u/' + beatmapset.creator_id;
            }

            var beatmapCreatorDiv = document.createElement("div");
            beatmapCreatorDiv.appendChild(beatmapCreator);
            beatmapCreatorDiv.appendChild(beatmapCreatorLink);
            addClass(beatmapCreatorDiv, "beatmap-creator");

            var hiddenElementsContainer = document.createElement("div");
            addClass(hiddenElementsContainer, "hidden-elements");

            var beatmapSource = document.createElement("div");
            var beatmapSourceContent = document.createElement("span");
            addClass(beatmapSource, "beatmap-source");
            hiddenElementsContainer.appendChild(beatmapSource);

            if (beatmapset.source) {
                setText(beatmapSourceContent, beatmapset.source);
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
                addClass(beatmapIcon, "beatmap-icon");
                beatmapIcon.src = getBeatmapIcon(beatmap);
                beatmapIcon.title = beatmap.version;
                beatmapIcon.alt = beatmap.version;
                beatmapIconLink.appendChild(beatmapIcon);
                beatmapIconLink.href = '/b/' + beatmap.id;
                hiddenElementsContainer.appendChild(beatmapIconLink);
            }

            beatmapInfoLeft.appendChild(beatmapLink);

            var beatmapInfoRight = document.createElement("div");
            addClass(beatmapInfoRight, "beatmap-stats");

            var beatmapTagsDiv = document.createElement("div");
            addClass(beatmapTagsDiv, "beatmap-tags");

            if (beatmapset.language_id > 0) {
                var languageTag = document.createElement("a");
                setText(languageTag, Languages.get(beatmapset.language_id).toString());
                beatmapTagsDiv.appendChild(languageTag);
            }

            if (beatmapset.genre_id > 0) {
                var genreTag = document.createElement("a");
                setText(genreTag, Genres.get(beatmapset.genre_id).toString().replace("_", " "));
                beatmapTagsDiv.appendChild(genreTag);
            }

            var ratingBar = document.createElement("div");
            ratingBar.style.width = (100 - ((beatmapset.rating_average / 10) * 100)) + '%';
            addClass(ratingBar, "beatmap-rating-bar");

            var beatmapRating = document.createElement("div");
            addClass(beatmapRating, "beatmap-rating");
            beatmapRating.appendChild(ratingBar);

            var dateText = document.createElement("span");
            var statusTimestamp = beatmapset.approved_at || beatmapset.last_update;
            var displayDate = formatDateShort(statusTimestamp);
            setText(dateText, displayDate);
            dateText.title = beatmapset.approved_at ? "Approved date" : "Last update";
            addClass(dateText, "hidden-elements");

            var heartIcon = document.createElement("i");
            addClasses(heartIcon, ["icon-heart"]);

            var playsIcon = document.createElement("i");
            addClasses(playsIcon, ["icon-play"]);

            var totalPlays = 0;
            for (var j = 0; j < beatmapset.beatmaps.length; j++) {
                totalPlays += beatmapset.beatmaps[j].playcount;
            }

            var detailsDiv = document.createElement("div");
            addClass(detailsDiv, "beatmap-details");
            detailsDiv.appendChild(dateText);
            detailsDiv.appendChild(heartIcon);
            detailsDiv.appendChild(document.createTextNode(beatmapset.favourite_count.toLocaleString()));
            detailsDiv.appendChild(playsIcon);
            detailsDiv.appendChild(document.createTextNode(totalPlays.toLocaleString()));

            beatmapInfoRight.appendChild(beatmapTagsDiv);
            beatmapInfoRight.appendChild(beatmapRating);
            beatmapInfoRight.appendChild(detailsDiv);

            beatmapsetDiv.appendChild(beatmapInfoLeft);
            beatmapsetDiv.appendChild(beatmapCreatorDiv);
            beatmapsetDiv.appendChild(beatmapInfoRight);
            beatmapsetDiv.appendChild(hiddenElementsContainer);
            beatmapContainer.appendChild(beatmapsetDiv);
        }

        $(".beatmapset").hover(
            function() {
                $(this).find(".beatmap-info").marquee({ speed: 50 });
                $(this).find(".hidden-elements").stop().fadeTo(1,100);
                $(this).find(".beatmap-side-options").clearQueue().stop().delay(500).animate({
                    width: 'show'
                }, 100);
            },
            function() {
                $(this).find(".beatmap-info").attr('stop', 1);
                $(this).find(".hidden-elements").fadeOut(400);
                $(this).find(".beatmap-side-options").clearQueue().stop().delay(500).animate({
                    width: 'hide'
                }, 100);
            }
        );

        totalBeatmaps += beatmapsets.length;
        currentPage++;
        busy = false;
    }, function(xhr) {
        clearStatusText();
        var errorText = document.createElement("h3");
        errorText.style.textAlign = "center";
        errorText.style.margin = "0 auto";
        errorText.id = "status-text";
        setText(errorText, "An error occurred while loading beatmaps.");

        beatmapContainer.appendChild(errorText);
        busy = false;
    });
}

function addFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites";

    performApiRequest("POST", url, {"set_id": beatmapsetId}, function(xhr) {
        var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
        heartIcon.parentNode.style.color = "red";
        heartIcon.parentNode.onclick = function(e) {
            preventEventDefault(e || window.event);
            removeFavorite(beatmapsetId);
        }
    }, function(xhr) {
        // Most likely already favorited, so just do the same thing
        var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
        heartIcon.parentNode.style.color = "red";
        heartIcon.parentNode.onclick = function(e) {
            preventEventDefault(e || window.event);
            removeFavorite(beatmapsetId);
        }
    });
}

function removeFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites/" + beatmapsetId;

    performApiRequest("DELETE", url, null, function(xhr) {
        var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
        heartIcon.parentNode.style.color = null;
        heartIcon.parentNode.onclick = function(e) {
            preventEventDefault(e || window.event);
            addFavorite(beatmapsetId);
        }
    });
}

function clearStatusText() {
    if (document.querySelectorAll == undefined) {
        var loadingText = document.getElementById("status-text");

        if (!loadingText)
            return;

        loadingText.parentNode.removeChild(loadingText);
        return;
    }

    var loadingTexts = document.querySelectorAll("#status-text");

    for (var i = 0; i < loadingTexts.length; i++) {
        loadingTexts[i].parentNode.removeChild(loadingTexts[i]);
    }
}

function setElement(element) {
    var dataName = element.parentNode.parentNode.getAttribute("data-name");
    var elements = element.parentNode.querySelectorAll("a");
    var removes = element.getAttribute("removes")

    if (removes) {
        var removeElement = document.querySelector('[data-name="' + removes + '"]');
        if (removeElement) {
            removeClass(removeElement, "selected");
        }
    }

    if (!dataName) {
        toggleClass(element, "selected");
        getBeatmapsets(true);
        return;
    }

    for (var i = 0; i < elements.length; i++) {
        if (elements[i] !== element) {
            removeClass(elements[i], "selected");
        }
    }

    toggleClass(element, "selected");

    if (!element.parentNode.querySelector(".selected")) {
        addClass(elements[0], "selected");
    }

    getBeatmapsets(true);
}

function setOrder(element) {
    var currentOrderSelection = document.querySelector(".beatmap-order-select img");
    var currentSortElement = currentOrderSelection.parentNode.querySelector("a");

    if (currentSortElement != element) {
        currentOrderSelection.parentNode.removeChild(currentOrderSelection);
    } else {
        currentOrderSelection.src = endsWith(currentOrderSelection.src, "/images/down.gif") ? "/images/up.gif" : "/images/down.gif";
        currentOrderSelection.alt = endsWith(currentOrderSelection.src, "/images/down.gif") ? "Descending" : "Ascending";
        getBeatmapsets(true);
        return;
    }

    var orderSelection = document.createElement("img");
    orderSelection.src = "/images/down.gif";
    orderSelection.alt = "Descending";
    getParentElement(element).appendChild(orderSelection);
    getBeatmapsets(true);
}

if (document.querySelectorAll !== undefined) {
    var beatmapOptionsLinks = document.querySelectorAll(".beatmap-options a");
    for (var i = 0; i < beatmapOptionsLinks.length; i++) {
        addEvent("click", beatmapOptionsLinks[i], function(event) {
            event = event || window.event;
            preventEventDefault(event);
            setElement(getEventTarget(event));
        });
    }
    
    var beatmapOrderSelectLinks = document.querySelectorAll(".beatmap-order-select a");
    for (var i = 0; i < beatmapOrderSelectLinks.length; i++) {
        addEvent("click", beatmapOrderSelectLinks[i], function(event) {
            event = event || window.event;
            preventEventDefault(event);
            setOrder(getEventTarget(event));
        });
    }
}

var input = document.getElementById("search-input");
var timeout = null;

addEvent('load', window, function(event) {
    getBeatmapsets(true);
});

addEvent("scroll", window, function(event) {
    if (getWindowHeight() + getScrollTop() >= document.body.offsetHeight / 1.4) {
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