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

    get: function (value) {
        var keys = $.map(this, function (v, i) {
            return i;
        });
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

    get: function (value) {
        var keys = $.map(this, function (v, i) {
            return i;
        });
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
    } else if (beatmap.diff < 2.7) {
        difficulty = "normal";
    } else if (beatmap.diff < 4) {
        difficulty = "hard";
    } else if (beatmap.diff < 5.3) {
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
        $(loadingText).text("Loading...");
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

    performApiRequest(
        "POST",
        "/beatmapsets/search",
        getSearchInput(),
        function (xhr) {
            var beatmapsets = JSON.parse(xhr.responseText);
            var loadingText = document.getElementById("status-text");

            if (loadingText) {
                loadingText.parentNode.removeChild(loadingText);
            }

            if (beatmapsets.length <= 0) {
                if (totalBeatmaps <= 0) {
                    var noMapsText = document.createElement("h3");
                    $(noMapsText).text("Nothing found... :(");
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
                $(beatmapsetDiv).addClass("beatmapset");
                beatmapsetDiv.id = "beatmapset-" + beatmapset.id;

                var lastUpdate = beatmapset.last_update;
                var lastUpdateTimestamp = Math.floor(Date.parse(lastUpdate) / 1000);

                var imageUrl = 'url("/mt/' + beatmapset.id + "?c=" + lastUpdateTimestamp + '")';

                // Use http for images if the page is not secure
                if (window.location.protocol != "https:") {
                    imageUrl = imageUrl.replace("https://", "http://");
                }

                var beatmapImage = document.createElement("div");
                $(beatmapImage).addClass("beatmap-image");
                beatmapImage.style.backgroundImage = imageUrl;

                var beatmapSideOptions = document.createElement("div");
                $(beatmapSideOptions).addClass("beatmap-side-options");
                beatmapSideOptions.style.display = "none";
                beatmapSideOptions.style.overflow = "hidden";
                beatmapSideOptions.style.width = "24px";

                var heartIcon = document.createElement("i");
                $(heartIcon).addClass("icon-heart");
                var favouriteLink = document.createElement("a");
                favouriteLink.href = "#";
                favouriteLink.appendChild(heartIcon);
                beatmapSideOptions.appendChild(favouriteLink);

                var speechBubbleIcon = document.createElement("i");
                $(speechBubbleIcon).addClass("icon-comment");
                var commentsLink = document.createElement("a");
                commentsLink.href = "/forum/t/" + beatmapset.topic_id;
                commentsLink.appendChild(speechBubbleIcon);
                beatmapSideOptions.appendChild(commentsLink);

                var downloadIcon = document.createElement("i");
                $(downloadIcon).addClass("icon-download-alt");
                var downloadLink = document.createElement("a");
                downloadLink.href = "/d/" + beatmapset.id;
                downloadLink.appendChild(downloadIcon);
                beatmapSideOptions.appendChild(downloadLink);

                if (beatmapset.server == 0) {
                    commentsLink.href = "https://osu.ppy.sh/beatmapsets/" + beatmapset.id + "#comments";
                }

                var playIcon = document.createElement("i");
                $(playIcon).addClass("icon-play");

                var lastUpdate = beatmapset.last_update;
                var lastUpdateTimestamp = Math.floor(Date.parse(lastUpdate) / 1000);

                var beatmapAudio = document.createElement("audio");
                beatmapAudio.src = "/mp3/preview/" + beatmapset.id + "?c=" + lastUpdateTimestamp;
                beatmapAudio.id = "beatmap-preview-" + beatmapset.id;
                beatmapAudio.volume = 0.5;

                (function (
                    currentBeatmapsetId,
                    currentPlayIcon,
                    currentFavouriteLink,
                    currentDownloadLink,
                    currentBeatmapAudio
                ) {
                    if (!currentUser) {
                        currentFavouriteLink.onclick = function (e) {
                            if (e) e.preventDefault();
                            showLoginForm();
                        };
                        currentDownloadLink.onclick = function (e) {
                            if (e) e.preventDefault();
                            showLoginForm();
                        };
                    } else {
                        currentFavouriteLink.onclick = function (e) {
                            if (e) e.preventDefault();
                            addFavorite(currentBeatmapsetId);
                        };
                    }

                    currentPlayIcon.onclick = function (e) {
                        var beatmapPreviewElements = document.querySelectorAll('[id^="beatmap-preview-"]');
                        for (var i = 0; i < beatmapPreviewElements.length; i++) {
                            var element = beatmapPreviewElements[i];

                            if (!element.paused && element.id !== "beatmap-preview-" + currentBeatmapsetId) {
                                element.pause();
                                element.currentTime = 0;

                                var audioPlayIcon = $(element).parent()[0].querySelector(".beatmap-image i");
                                $(audioPlayIcon).removeClass("icon-pause");
                                $(audioPlayIcon).addClass("icon-play");
                            }
                        }

                        resetOrPlayAudio("beatmap-preview-" + currentBeatmapsetId);
                        var audio = document.getElementById("beatmap-preview-" + currentBeatmapsetId);

                        if (audio.paused) {
                            $(currentPlayIcon).removeClass("icon-pause");
                            $(currentPlayIcon).addClass("icon-play");
                        } else {
                            $(currentPlayIcon).removeClass("icon-play");
                            $(currentPlayIcon).addClass("icon-pause");
                        }
                    };

                    currentBeatmapAudio.onended = function () {
                        $(currentPlayIcon).removeClass("icon-pause");
                        $(currentPlayIcon).addClass("icon-play");
                    };
                })(beatmapset.id, playIcon, favouriteLink, downloadLink, beatmapAudio);

                beatmapImage.appendChild(playIcon);
                beatmapsetDiv.appendChild(beatmapImage);
                beatmapsetDiv.appendChild(beatmapAudio);
                beatmapsetDiv.appendChild(beatmapSideOptions);

                var beatmapInfoLeft = document.createElement("div");
                $(beatmapInfoLeft).addClass("beatmap-info");

                var beatmapArtist = document.createElement("span");
                $(beatmapArtist).text(beatmapset.artist);
                beatmapArtist.style.color = "#555555";

                var beatmapTitle = document.createElement("span");
                $(beatmapTitle).addClass("beatmap-title");
                $(beatmapTitle).text(beatmapset.title);

                var beatmapLink = document.createElement("a");
                $(beatmapLink).addClass("beatmap-link");
                beatmapLink.href = "/s/" + beatmapset.id;
                beatmapLink.appendChild(beatmapArtist);
                beatmapLink.appendChild(document.createTextNode(" - "));
                beatmapLink.appendChild(beatmapTitle);

                var beatmapInfoLeft = document.createElement("div");
                $(beatmapInfoLeft).addClass("beatmap-info");

                var videoIcon = document.createElement("i");
                $(videoIcon).addClass("icon-film");

                var imageIcon = document.createElement("i");
                $(imageIcon).addClass("icon-picture");

                if (beatmapset.has_video) {
                    beatmapInfoLeft.appendChild(videoIcon);
                }
                if (beatmapset.has_storyboard) {
                    beatmapInfoLeft.appendChild(imageIcon);
                }

                var beatmapCreator = document.createElement("span");
                $(beatmapCreator).text("mapped by ");

                var beatmapCreatorLink = document.createElement("a");
                $(beatmapCreatorLink).text(beatmapset.creator);
                if (beatmapset.server === 0) {
                    beatmapCreatorLink.href = "https://osu.ppy.sh/u/" + beatmapset.creator;
                } else {
                    beatmapCreatorLink.href = "/u/" + beatmapset.creator_id;
                }

                var beatmapCreatorDiv = document.createElement("div");
                beatmapCreatorDiv.appendChild(beatmapCreator);
                beatmapCreatorDiv.appendChild(beatmapCreatorLink);
                $(beatmapCreatorDiv).addClass("beatmap-creator");

                var hiddenElementsContainer = document.createElement("div");
                $(hiddenElementsContainer).addClass("hidden-elements");

                var beatmapSource = document.createElement("div");
                var beatmapSourceContent = document.createElement("span");
                $(beatmapSource).addClass("beatmap-source");
                hiddenElementsContainer.appendChild(beatmapSource);

                if (beatmapset.source) {
                    $(beatmapSourceContent).text(beatmapset.source);
                    beatmapSource.appendChild(document.createTextNode("from "));
                    beatmapSource.appendChild(beatmapSourceContent);
                }

                // Order beatmaps by difficulty and mode
                beatmapset.beatmaps.sort(function (a, b) {
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
                    $(beatmapIcon).addClass("beatmap-icon");
                    beatmapIcon.src = getBeatmapIcon(beatmap);
                    beatmapIcon.title = beatmap.version;
                    beatmapIcon.alt = beatmap.version;
                    beatmapIconLink.appendChild(beatmapIcon);
                    beatmapIconLink.href = "/b/" + beatmap.id;
                    hiddenElementsContainer.appendChild(beatmapIconLink);
                }

                beatmapInfoLeft.appendChild(beatmapLink);

                var beatmapInfoRight = document.createElement("div");
                $(beatmapInfoRight).addClass("beatmap-stats");

                var beatmapTagsDiv = document.createElement("div");
                $(beatmapTagsDiv).addClass("beatmap-tags");

                if (beatmapset.language_id > 0) {
                    var languageTag = document.createElement("a");
                    $(languageTag).text(Languages.get(beatmapset.language_id).toString());
                    beatmapTagsDiv.appendChild(languageTag);
                }

                if (beatmapset.genre_id > 0) {
                    var genreTag = document.createElement("a");
                    $(genreTag).text(Genres.get(beatmapset.genre_id).toString().replace("_", " "));
                    beatmapTagsDiv.appendChild(genreTag);
                }

                var ratingBar = document.createElement("div");
                ratingBar.style.width = 100 - (beatmapset.rating_average / 10) * 100 + "%";
                $(ratingBar).addClass("beatmap-rating-bar");

                var beatmapRating = document.createElement("div");
                $(beatmapRating).addClass("beatmap-rating");
                beatmapRating.appendChild(ratingBar);

                var dateText = document.createElement("span");
                var statusTimestamp = beatmapset.approved_at || beatmapset.last_update;
                var displayDate = formatDateShort(statusTimestamp);
                $(dateText).text(displayDate);
                dateText.title = beatmapset.approved_at ? "Approved date" : "Last update";
                $(dateText).addClass("hidden-elements");

                var heartIcon = document.createElement("i");
                $(heartIcon).addClass("icon-heart");

                var playsIcon = document.createElement("i");
                $(playsIcon).addClass("icon-play");

                var totalPlays = 0;
                for (var j = 0; j < beatmapset.beatmaps.length; j++) {
                    totalPlays += beatmapset.beatmaps[j].playcount;
                }

                var detailsDiv = document.createElement("div");
                $(detailsDiv).addClass("beatmap-details");
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
                function () {
                    $(this).find(".beatmap-info").marquee({ speed: 50 });
                    $(this).find(".hidden-elements").stop().fadeTo(1, 100);
                    $(this).find(".beatmap-side-options").clearQueue().stop().delay(500).animate(
                        {
                            width: "show"
                        },
                        100
                    );
                },
                function () {
                    $(this).find(".beatmap-info").attr("stop", 1);
                    $(this).find(".hidden-elements").fadeOut(400);
                    $(this).find(".beatmap-side-options").clearQueue().stop().delay(500).animate(
                        {
                            width: "hide"
                        },
                        100
                    );
                }
            );

            totalBeatmaps += beatmapsets.length;
            currentPage++;
            busy = false;
        },
        function (xhr) {
            clearStatusText();
            var errorText = document.createElement("h3");
            errorText.style.textAlign = "center";
            errorText.style.margin = "0 auto";
            errorText.id = "status-text";
            $(errorText).text("An error occurred while loading beatmaps.");

            beatmapContainer.appendChild(errorText);
            busy = false;
        }
    );
}

function addFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites";

    performApiRequest(
        "POST",
        url,
        { set_id: beatmapsetId },
        function (xhr) {
            var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
            heartIcon.parentNode.style.color = "red";
            heartIcon.parentNode.onclick = function (e) {
                if (e) e.preventDefault();
                removeFavorite(beatmapsetId);
            };
        },
        function (xhr) {
            // Most likely already favorited, so just do the same thing
            var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
            heartIcon.parentNode.style.color = "red";
            heartIcon.parentNode.onclick = function (e) {
                if (e) e.preventDefault();
                removeFavorite(beatmapsetId);
            };
        }
    );
}

function removeFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites/" + beatmapsetId;

    performApiRequest("DELETE", url, null, function (xhr) {
        var heartIcon = document.querySelector("#beatmapset-" + beatmapsetId + " .icon-heart");
        heartIcon.parentNode.style.color = null;
        heartIcon.parentNode.onclick = function (e) {
            if (e) e.preventDefault();
            addFavorite(beatmapsetId);
        };
    });
}

function clearStatusText() {
    if (document.querySelectorAll == undefined) {
        var loadingText = document.getElementById("status-text");

        if (!loadingText) return;

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
    var removes = element.getAttribute("removes");

    if (removes) {
        var removeElement = document.querySelector('[data-name="' + removes + '"]');
        if (removeElement) {
            $(removeElement).removeClass("selected");
        }
    }

    if (!dataName) {
        $(element).toggleClass("selected");
        getBeatmapsets(true);
        return;
    }

    for (var i = 0; i < elements.length; i++) {
        if (elements[i] !== element) {
            $(elements[i]).removeClass("selected");
        }
    }

    $(element).toggleClass("selected");

    if (!element.parentNode.querySelector(".selected")) {
        $(elements[0]).addClass("selected");
    }

    getBeatmapsets(true);
}

function setOrder(element) {
    var currentOrderSelection = document.querySelector(".beatmap-order-select img");
    var currentSortElement = currentOrderSelection.parentNode.querySelector("a");

    if (currentSortElement != element) {
        currentOrderSelection.parentNode.removeChild(currentOrderSelection);
    } else {
        currentOrderSelection.src = endsWith(currentOrderSelection.src, "/images/down.gif")
            ? "/images/up.gif"
            : "/images/down.gif";
        currentOrderSelection.alt = endsWith(currentOrderSelection.src, "/images/down.gif")
            ? "Descending"
            : "Ascending";
        getBeatmapsets(true);
        return;
    }

    var orderSelection = document.createElement("img");
    orderSelection.src = "/images/down.gif";
    orderSelection.alt = "Descending";
    $(element).parent()[0].appendChild(orderSelection);
    getBeatmapsets(true);
}

if (document.querySelectorAll !== undefined) {
    var beatmapOptionsLinks = document.querySelectorAll(".beatmap-options a");
    for (var i = 0; i < beatmapOptionsLinks.length; i++) {
        $(beatmapOptionsLinks[i]).on("click", function (event) {
            event = event || window.event;
            event.preventDefault();
            setElement(event.target || event.srcElement);
        });
    }

    var beatmapOrderSelectLinks = document.querySelectorAll(".beatmap-order-select a");
    for (var i = 0; i < beatmapOrderSelectLinks.length; i++) {
        $(beatmapOrderSelectLinks[i]).on("click", function (event) {
            event = event || window.event;
            event.preventDefault();
            setOrder(event.target || event.srcElement);
        });
    }
}

var input = document.getElementById("search-input");
var timeout = null;

$(window).on("load", function (event) {
    getBeatmapsets(true);
});

$(window).on("scroll", function (event) {
    if (getWindowHeight() + getScrollTop() >= document.body.offsetHeight / 1.4) {
        getBeatmapsets(false);
    }
});

$(input).on("keyup", function (event) {
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
        getBeatmapsets(true);
    }, 500);
});
