var activeTab = window.location.hash !== "" ? window.location.hash.replace("#", "") : "general";
var topLeaderOffset = 0;
var topScoreOffset = 0;

function pinScore(scoreId, userId) {
    var url = "/users/" + currentUser + "/pinned";
    performApiRequest("POST", url, {"score_id": scoreId}, function() {
        loadPinnedScores(userId, modeName);
    });
}

function unpinScore(scoreId, userId) {
    var url = "/users/" + currentUser + "/pinned";
    performApiRequest("DELETE", url, {"score_id": scoreId}, function() {
        loadPinnedScores(userId, modeName);
    });
}

function expandProfileTab(id, forceExpand) {
    var tab = document.getElementById(id);
    activeTab = id;

    if (!tab) {
        expandProfileTab(id.startsWith("score-top") ? "leader" : "general", forceExpand);
        return;
    }

    // Check for 'expanded' class
    if (tab.className.indexOf("expanded") === -1 || forceExpand) {
        tab.style.display = "block";

        if (tab.style.height === "0px") {
            slideDown(tab);
        }

        if (forceExpand) {
            window.location.hash = "#" + activeTab;
        }

        // Apply class after slide animation is done
        setTimeout(function() { tab.className += " expanded" }, 500);
    } else {
        slideUp(tab);
        tab.className = tab.className.replace(/(?:^|\s)expanded(?!\S)/, '');
    }

    if (activeTab === 'general') {
        loadUserPerformanceGraph(userId, modeName);
    } else if (activeTab === 'history') {
        loadUserPlaysGraph(userId, modeName);
        loadUserViewsGraph(userId, modeName);
    }
}

function expandRecentActivity() {
    var recentPreview = document.getElementById("profile-recent-preview");
    var recentFull = document.getElementById("profile-recent-full");
    var general = document.getElementById("general");

    recentPreview.style.display = "none";
    recentFull.style.display = "block";
    slideDown(general);
}

function createScoreElement(score, index, type) {
    var scoreDiv = document.createElement("div");
    scoreDiv.id = "score-" + type + "-" + index;
    scoreDiv.className = "score";

    var scoreTable = document.createElement("table");
    var tableBody = document.createElement("tbody");
    var tableRow = document.createElement("tr");

    var leftColumn = document.createElement("td");
    leftColumn.className = 'score-left';

    var scoreGrade = document.createElement("img");
    scoreGrade.src = "/images/grades/" + score.grade + "_small.png";
    scoreGrade.loading = "lazy";

    var beatmapInfo = document.createElement("a");
    beatmapInfo.href = "/b/" + score.beatmap.id + "?mode=" + score.mode;
    beatmapInfo.innerText = score.beatmap.beatmapset.artist + " - " + score.beatmap.beatmapset.title + " [" + score.beatmap.version + "]";

    var modsText = document.createElement("b");
    if (score.mods > 0) {
        modsText.innerText = "+" + Mods.getString(score.mods);
    }

    var scoreInfo = document.createElement("b");
    scoreInfo.appendChild(beatmapInfo);
    scoreInfo.appendChild(modsText);

    var accuracyText = document.createTextNode("(" + (score.acc * 100).toFixed(2) + "%)");

    // Parse date to a format that timeago can understand
    var scoreDate = new Date(score.submitted_at);
    var scoreDateString = scoreDate.toLocaleDateString(
        "en-us", {
            year: "numeric",
            month: "numeric",
            day: "numeric",
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            timeZoneName: "short"
        }
    );

    var rightColumn = document.createElement("td");
    rightColumn.className = 'score-right';

    var ppText = document.createElement("b");
    ppText.innerText = (score.pp.toFixed(0) + "pp");

    var ppDisplay = document.createElement("div");
    ppDisplay.className = "pp-display";
    ppDisplay.appendChild(ppText);

    var ppWeightPercent = document.createElement("b");
    ppWeightPercent.innerText = (Math.pow(0.95, index + topScoreOffset) * 100).toFixed(0) + "%";

    var ppWeight = document.createElement("div");
    ppWeight.className = "pp-display-weight";

    if (type == "top") {
        ppWeight.appendChild(document.createTextNode("weighted "));
        ppWeight.appendChild(ppWeightPercent);
        ppWeight.appendChild(document.createTextNode(" (" + (score.pp * Math.pow(0.95, index + topScoreOffset)).toFixed(0) + "pp)"));
    }

    if (!approvedRewards && score.beatmap.status > 2) {
        // Display heart icon for loved maps
        ppText.innerHTML = '<i class="fa-regular fa-heart"></i>';
        ppText.title = score.pp.toFixed(0) + "pp (if ranked)";
        // Reset pp weight text
        ppWeight.innerHTML = (type == "top" ? "weighted <b>0%</b> (0pp)" : "");
    }

    var iconContainer = document.createElement("div");
    iconContainer.className = "score-icon-container";

    var scoreInfoDiv = document.createElement("div");
    scoreInfoDiv.appendChild(scoreGrade);
    scoreInfoDiv.appendChild(scoreInfo);
    scoreInfoDiv.appendChild(accuracyText);
    
    var scoreBottomDiv = document.createElement('div');
    scoreBottomDiv.classList.add('score-bottom');

    // Score's Date
    var dateText = document.createElement("time");
    dateText.setAttribute("datetime", score.submitted_at);
    dateText.innerText = score.submitted_at;
    dateText.title = scoreDateString;
    dateText.className = "timeago";

    scoreBottomDiv.appendChild(dateText);

    // Score's Client Version
    var versionText = false;
    if (typeof(score.client_version) == 'string') {
        versionText = score.client_version; // If it's a string, b will already be prepended
    } else if (typeof(score.client_version) == 'number') {
        versionText = "b" + score.client_version.toString();
    }
    
    if (versionText != false) {
        var clientText = document.createElement('div');
        clientText.classList.add('score-version');
        clientText.innerHTML += ' &mdash; on ';
    
        var clientTextVersion = document.createElement('span');
        clientTextVersion.classList.add('score-version-number');
        clientTextVersion.innerText = versionText;

        clientText.appendChild(clientTextVersion);
        scoreBottomDiv.appendChild(clientText);
    }

    var replayLink = document.createElement('a');
    replayLink.href = "/scores/" + score.id + "/download";
    replayLink.className = "score-replay";
    replayLink.title = "Download Replay";
    replayLink.target = "_blank";

    var replayIcon = document.createElement("i");
    replayIcon.className = "fa-regular fa-download";
    replayLink.appendChild(replayIcon);

    iconContainer.appendChild(replayLink);

    if (currentUser === userId) {
        var pinIcon = document.createElement("i");
        pinIcon.className = "fa-regular fa-star score-pin-" + score.id;

        if (!score.pinned) {
            pinIcon.className += " score-pin-icon";
            pinIcon.title = "Pin Score";
            pinIcon.onclick = function() {
                var icons = document.querySelectorAll(".score-pin-" + score.id);
                for (var j = 0; j < icons.length; j++) {
                    icons[j].classList.remove("score-pin-icon");
                    icons[j].classList.add("score-pinned-icon");
                    icons[j].title = "Unpin Score";
                }
                pinScore(score.id, userId);
                pinIcon.onclick = function() {
                    unpinScore(score.id, userId);
                    pinIcon.classList.remove("score-pinned-icon");
                    pinIcon.classList.add("score-pin-icon");
                    pinIcon.title = "Pin Score";
                };
            };
        } else {
            pinIcon.className += " score-pinned-icon";
            pinIcon.title = "Unpin Score";
            pinIcon.onclick = function() {
                var icons = document.querySelectorAll(".score-pin-" + score.id);
                for (var j = 0; j < icons.length; j++) {
                    icons[j].classList.remove("score-pinned-icon");
                    icons[j].classList.add("score-pin-icon");
                    icons[j].title = "Pin Score";
                }
                unpinScore(score.id, userId);
                pinIcon.onclick = function() {
                    pinScore(score.id, userId);
                    pinIcon.classList.remove("score-pin-icon");
                    pinIcon.classList.add("score-pinned-icon");
                    pinIcon.title = "Unpin Score";
                };
            };
        }

        iconContainer.appendChild(pinIcon);
    }

    ppWeight.appendChild(iconContainer);
    leftColumn.appendChild(scoreInfoDiv);
    leftColumn.appendChild(scoreBottomDiv);
    rightColumn.appendChild(ppDisplay);
    rightColumn.appendChild(ppWeight);
    tableRow.appendChild(leftColumn);
    tableRow.appendChild(rightColumn);
    tableBody.appendChild(tableRow);
    scoreTable.appendChild(tableBody);
    scoreDiv.appendChild(scoreTable);

    return scoreDiv;
}

function loadPinnedScores(userId, mode) {
    var url = "/users/" + userId + "/pinned/" + mode;
    var scoreContainer = document.getElementById("pinned-scores");

    performApiRequest("GET", url, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var loadingText = document.getElementById("pinned-scores-loading");
        var scores = data.scores;

        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }

        // Reset container
        scoreContainer.innerHTML = "<h2>Pinned Scores</h2>";

        if (data.total <= 0) {
            scoreContainer.appendChild(
                document.createTextNode("This player has not pinned any scores yet :(")
            );
            return;
        }

        // Update total score count
        var heading = document.getElementById('pinned-scores').getElementsByTagName('h2')[0];
        heading.innerHTML = 'Pinned Scores (' + data.total.toLocaleString() + ')'

        for (var index = 0; index < scores.length; index++) {
            var score = scores[index];
            var scoreDiv = createScoreElement(score, index, "pinned");
            scoreContainer.appendChild(scoreDiv);
        }

        // Render timeago elements
        renderTimeagoElements();

        slideDown(document.getElementById("leader"));
    }, function(xhr) {
        var errorText = document.createElement("p");
        errorText.innerText = "Failed to load pinned scores.";
        errorText.classList.add("score");
        scoreContainer.appendChild(errorText);

        var loadingText = document.getElementById("pinned-scores-loading");
        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }
    });
}

function loadTopPlays(userId, mode, limit, offset) {
    var url = "/users/" + userId + "/top/" + mode + "?limit=" + limit + "&offset=" + offset;
    var scoreContainer = document.getElementById("top-scores");

    performApiRequest("GET", url, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var loadingText = document.getElementById("top-scores-loading");
        var scores = data.scores;

        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }

        if (data.total <= 0) {
            var noScoresText = document.createElement("p");
            noScoresText.innerText = "No awesome performance records yet :(";
            scoreContainer.appendChild(noScoresText);
            return;
        }

        // Update total score count
        var heading = document.getElementById('top-scores').getElementsByTagName('h2')[0];
        heading.innerHTML = 'Best Performance (' + data.total.toLocaleString() + ')';

        for (var index = 0; index < scores.length; index++) {
            var score = scores[index];
            if (score.beatmap.status > 2 && !approvedRewards) {
                continue;
            }

            var scoreDiv = createScoreElement(score, index, "top");
            scoreContainer.appendChild(scoreDiv);
        }
        topScoreOffset += scores.length;

        // Render timeago elements
        renderTimeagoElements();

        if (scores.length >= limit) {
            // Create show more text
            var showMoreText = document.createElement("b");
            showMoreText.innerText = "Show me more!";

            // Add onclick event
            var showMoreHref = document.createElement("a");
            showMoreHref.href = "#score-top-" + scores.length;
            showMoreHref.id = "show-more-top";
            showMoreHref.appendChild(showMoreText);
            showMoreHref.onclick = function() {
                var loadingText = document.createElement("p");
                loadingText.innerText = "Loading...";
                loadingText.id = "top-scores-loading";

                var showMore = document.getElementById("show-more-top");
                showMore.parentElement.appendChild(loadingText);
                showMore.remove();

                loadTopPlays(userId, modeName, 50, topScoreOffset);
            };

            // Create wrapper that contains styling
            var showMore = document.createElement("div");
            showMore.className = "score show-more";
            showMore.appendChild(showMoreHref);

            // Append show more text to container
            scoreContainer.appendChild(showMore);
        }

        slideDown(document.getElementById("leader"));
    }, function(xhr) {
        var errorText = document.createElement("p");
        errorText.innerText = "Failed to load top plays.";
        errorText.classList.add("score");
        scoreContainer.appendChild(errorText);

        var loadingText = document.getElementById("top-scores-loading");

        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }
    });

    return false;
}

function loadLeaderScores(userId, mode, limit, offset) {
    var url = "/users/" + userId + "/first/" + mode + "?limit=" + limit + "&offset=" + offset;
    var scoreContainer = document.getElementById("leader-scores");

    performApiRequest("GET", url, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var loadingText = document.getElementById("leader-scores-loading");
        var scores = data.scores;

        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }

        if (data.total <= 0) {
            var noScoresText = document.createElement("p");
            noScoresText.innerText = "No first place records currently :(";
            scoreContainer.appendChild(noScoresText);
            return;
        }

        // Update total score count
        var heading = document.getElementById('leader-scores').getElementsByTagName('h2')[0]
        heading.innerText = 'First Place Ranks (' + data.total.toLocaleString() + ')';

        for (var i = 0; i < scores.length; i++) {
            var scoreDiv = createScoreElement(scores[i], i, "leader");
            scoreContainer.appendChild(scoreDiv);
        }
        topLeaderOffset += scores.length;

        // Render timeago elements
        renderTimeagoElements();

        if (scores.length >= limit) {
            var showMoreText = document.createElement("b");
            showMoreText.innerText = "Show me more!";

            // Add onclick event
            var showMoreHref = document.createElement("a");
            showMoreHref.href = "#score-leader-" + scores.length;
            showMoreHref.id = "show-more-leader";
            showMoreHref.appendChild(showMoreText);
            showMoreHref.onclick = function() {
                var loadingText = document.createElement("p");
                loadingText.innerText = "Loading...";
                loadingText.id = "leader-scores-loading";

                var showMore = document.getElementById("show-more-leader");
                showMore.parentElement.appendChild(loadingText);
                showMore.remove();

                loadLeaderScores(userId, modeName, 50, topLeaderOffset);
            };

            // Create wrapper that contains styling
            var showMore = document.createElement("div");
            showMore.className = "score show-more";
            showMore.appendChild(showMoreHref);

            // Append show more text to container
            scoreContainer.appendChild(showMore);
        }

        slideDown(document.getElementById("leader"));
    }, function(xhr) {
        var errorText = document.createElement("p");
        errorText.innerText = "Failed to load first place ranks.";
        errorText.classList.add("score");
        scoreContainer.appendChild(errorText);

        var loadingText = document.getElementById("leader-scores-loading");
        if (loadingText) {
            loadingText.parentElement.classList.remove("score");
            loadingText.remove();
        }
    });

    return false;
}

function loadMostPlayed(userId, limit, offset) {
    var loadingText = document.getElementById("plays-loading");

    if (!loadingText)
        return;

    var url = "/users/" + userId + "/plays" + "?limit=" + limit + "&offset=" + offset;
    var playsContainer = document.getElementById("plays-container");

    performApiRequest("GET", url, null, function(xhr) {
        var plays = JSON.parse(xhr.responseText);
        if (plays.length <= 0) {
            playsContainer.appendChild(
                document.createTextNode("This player has not played anything yet :(")
            );
            return;
        }

        for (var index = 0; index < plays.length; index++) {
            var item = plays[index];
            var beatmapLink = document.createElement("a");
            beatmapLink.innerText = item.beatmap.beatmapset.artist + " - " + item.beatmap.beatmapset.title + " [" + item.beatmap.version + "]";
            beatmapLink.href = "/b/" + item.beatmap.id;

            var playsDiv = document.createElement("div");
            playsDiv.style.fontSize = (180 * Math.pow(0.95, index + 1)) + "%";
            playsDiv.style.margin = "2.5px";
            playsDiv.appendChild(
                document.createTextNode(item.count + " plays - ")
            );
            playsDiv.appendChild(beatmapLink);

            playsContainer.appendChild(playsDiv);
        }

        slideDown(document.getElementById("history"));
    });

    loadingText.remove();
}

function loadRecentPlays(userId, mode) {
    var loadingText = document.getElementById("recent-loading");

    if (!loadingText)
        return;

    var url = "/users/" + userId + "/recent/" + mode;
    var playsContainer = document.getElementById("recent-container");

    performApiRequest("GET", url, null, function(xhr) {
        var scores = JSON.parse(xhr.responseText);
        if (scores.length <= 0) {
            playsContainer.appendChild(
                document.createTextNode("No recent scores set by this player :(")
            );
            return;
        }

        for (var i = 0; i < scores.length; i++) {
            var score = scores[i];

            // Parse date to a format that timeago can understand
            var scoreDate = new Date(score.submitted_at);
            var scoreDateString = scoreDate.toLocaleDateString("en-us", {
                year: "numeric",
                month: "numeric",
                day: "numeric",
                hour: "numeric",
                minute: "numeric",
                second: "numeric",
                timeZoneName: "short",
            });

            var dateText = document.createElement("time");
            dateText.setAttribute("datetime", score.submitted_at);
            dateText.innerText = score.submitted_at;
            dateText.title = scoreDateString;
            dateText.className += " timeago";

            var beatmapLink = document.createElement("a");
            beatmapLink.innerText = score.beatmap.beatmapset.artist + " - " + score.beatmap.beatmapset.title + " [" + score.beatmap.version + "]";
            beatmapLink.href = "/b/" + score.beatmap.id;

            var modsText = "";

            if (score.mods > 0)
                modsText = "+" + Mods.getString(score.mods);

            var scoreDiv = document.createElement("div");
            scoreDiv.appendChild(dateText);
            scoreDiv.appendChild(document.createTextNode(" - "));
            scoreDiv.appendChild(beatmapLink);
            scoreDiv.appendChild(document.createTextNode(" " + Math.round(score.pp).toLocaleString('en-US') + "pp (" + score.grade + ") " + modsText));
            scoreDiv.style.margin = "2.5px";

            playsContainer.appendChild(scoreDiv);
        }

        // Render timeago elements
        renderTimeagoElements();

        // Slide down tab
        slideDown(document.getElementById("history"));
    });

    loadingText.parentNode.removeChild(loadingText);
}

function processRankEntries (entries, var_name, use_linear) {
    if (use_linear == undefined || use_linear == null) {
        use_linear = false;
    }

    var mapped_entry_array = entries;
    
    if (use_linear) {
        var best_entry_by_date = [];
        var current_date = null;
        var best = null;
        for (var i=0; i<entries.length; i++) {
            var entry = entries[i];
            var entry_date = new Date(entry.time);

            if (current_date == null) {
                current_date = entry_date;
                best = entry
            } else if (entry_date.getDate() == current_date.getDate() && entry_date.getMonth() && entry_date.getFullYear()) {
                if (entry[var_name] < best[var_name]) {
                    best = entry;
                }
            } else {
                best_entry_by_date.push(best);
                current_date = entry_date;
                best = entry;
            }
        }

        if (current_date != null && best != null) {
            best_entry_by_date.push(best);
        }

        mapped_entry_array = best_entry_by_date;
    }

    return mapped_entry_array.map(function(entry) {
        var difference = (Date.now() - Date.parse(entry.time));
        var elapsedDays = Math.ceil(difference / (1000 * 3600 * 24));
        return {
            x: -elapsedDays,
            y: -entry[var_name]
        };
    });
}

function processRankHistory(entries, use_linear) {
    if (use_linear == undefined || use_linear == null) {
        use_linear = false;
    }

    var globalRankValues = processRankEntries(entries, 'global_rank', use_linear);
    var scoreRankValues = processRankEntries(entries, 'score_rank', use_linear);
    var countryRankValues = processRankEntries(entries, 'country_rank', use_linear);
    var ppv1RankValues = processRankEntries(entries, 'ppv1_rank', use_linear);

    if (entries.length > 0) {
        countryRankValues.unshift({
            x: 0,
            y: -countryRank
        });
        globalRankValues.unshift({
            x: 0,
            y: -globalRank
        });
        scoreRankValues.unshift({
            x: 0,
            y: -scoreRank
        });
        ppv1RankValues.unshift({
            x: 0,
            y: -ppv1Rank
        });
    }

    ppv1RankValues = ppv1RankValues.filter(function(e) {
        return e.y != 0;
    });
    scoreRankValues = scoreRankValues.filter(function(e) {
        return e.y != 0;
    });
    globalRankValues = globalRankValues.filter(function(e) {
        return e.y != 0;
    });
    countryRankValues = countryRankValues.filter(function(e) {
        return e.y != 0;
    });

    ppv1RankValues = ppv1RankValues.reverse();
    scoreRankValues = scoreRankValues.reverse();
    globalRankValues = globalRankValues.reverse();
    countryRankValues = countryRankValues.reverse();

    return [{
            values: globalRankValues,
            key: 'Global Rank',
            color: '#ff7f0e'
        },
        {
            values: countryRankValues,
            key: 'Country Rank',
            color: '#0ec7ff',
            disabled: true
        },
        {
            values: scoreRankValues,
            key: 'Score Rank',
            color: '#d30eff',
            disabled: true
        },
        {
            values: ppv1RankValues,
            key: 'PPv1 Rank',
            color: '#51f542',
            disabled: true
        }
    ];
}

function resetUserPerformanceGraph () {
    $('#rank-graph svg')[0].innerHTML = '';
}

function loadUserPerformanceGraph(userId, mode, use_linear) {
    if (use_linear == undefined || use_linear == null) {
        use_linear = false;
    }

    resetUserPerformanceGraph();

    var interpolation = use_linear ? 'linear' : 'step';
    var url = '/users/' + userId + '/history/rank/' + mode;

    performApiRequest("GET", url, null, function(xhr) {
        var entries = JSON.parse(xhr.responseText);
        var rankData = processRankHistory(entries, use_linear);

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .margin({
                    left: 80,
                    bottom: 20,
                    right: 50
                })
                .useInteractiveGuideline(true)
                .transitionDuration(250)
                .interpolate(interpolation)
                .showLegend(true)
                .showYAxis(true)
                .showXAxis(true);

            chart.xAxis
                .axisLabel("Days")
                .tickFormat(function(days) {
                    if (days == 0) return "now";
                    if (days > 0) return (days != 1) ? 'In ' + days + ' days' : 'In ' + days + ' day';
                    return (days != -1) ? (-days) + ' days ago' : (-days) + ' day ago';
                });

            chart.yAxis
                .axisLabel("Rank")
                .tickFormat(function(rank) {
                    rank = Math.round(rank);
                    if (rank >= 0) return "";
                    return '#' + (-rank);
                });

            // Calculate the relative min/max user rank to display on y axis
            var ranks = [];

            for (var i = 0; i < rankData.length; i++) {
                for (var j = 0; j < rankData[i].values.length; j++) {
                    ranks.push(-rankData[i].values[j].y);
                }
            }

            var minRank = Math.min.apply(null, ranks);
            var maxRank = Math.max.apply(null, ranks);
            var userDigits = (maxRank.toString().length - 1);

            var minRankDigits = '1' + ((userDigits > 0) ? (userDigits) * '0' : '');
            var relativeMinRank = Math.round(minRank / (minRankDigits)) * minRankDigits;

            var maxRankDigits = '1' + (userDigits * '0');
            var relativeMaxRank = Math.round(maxRank / (maxRankDigits)) * maxRankDigits;

            var betweenRank = (relativeMaxRank - relativeMaxRank / 2);

            chart.yScale(d3.scale.linear().domain([-relativeMinRank - 1, -relativeMaxRank]));
            chart.xScale(d3.scale.linear().domain([-90, 0]));

            // Force chart to show range of x, y values
            chart.forceY([-relativeMinRank - 1, -relativeMaxRank]);

            // Only display certain tick values
            chart.xAxis.tickValues([-90, -60, -30, 0]);
            chart.yAxis.tickValues([-relativeMaxRank, -betweenRank, -relativeMinRank]);

            d3.select("#rank-graph svg")
                .datum(rankData)
                .call(chart);

            nv.utils.windowResize(function() {
                chart.update();
            });

            // Reset "dy" value
            var noDataElements = document.querySelectorAll('.nv-noData');
            for (var i = 0; i < noDataElements.length; i++) {
                noDataElements[i].setAttribute('dy', 0);
            }

            return chart;
        });
    });
}

function processPlayHistory(entries) {
    var values = [];
    for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        var start = new Date();
        var end = new Date();
        end.setFullYear(entry.year, entry.month - 1);

        var years = start.getFullYear() - end.getFullYear();
        var months = start.getMonth() - end.getMonth();

        var elapsedMonths = years * 12 + months;
        values.push({
            x: -elapsedMonths,
            y: entry.plays
        });
    }

    values.reverse();

    return [{
        values: values,
        key: 'Plays',
        color: '#f5f242',
        area: true
    }];
}

function loadUserPlaysGraph(userId, mode) {
    var url = "/users/" + userId + "/history/plays/" + mode;

    performApiRequest("GET", url, null, function(xhr) {
        var entries = JSON.parse(xhr.responseText);
        var playData = processPlayHistory(entries);

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .margin({
                    left: 80,
                    bottom: 20,
                    right: 50
                })
                .useInteractiveGuideline(true)
                .transitionDuration(250)
                .interpolate("linear")
                .showLegend(false)
                .showYAxis(true)
                .showXAxis(true);

            chart.xAxis
                .axisLabel("Months")
                .tickFormat(function(month) {
                    if (month % 1 !== 0) return "";
                    if (month == 0) return "This Month";
                    if (month > 0) return (month != 1) ? "In " + month + " months" : "In " + month + " month";
                    return (month != -1) ? (-month) + " months ago" : (-month) + " month ago";
                });

            chart.yAxis
                .axisLabel("Plays")
                .tickFormat(function(plays) {
                    plays = Math.round(plays);
                    return plays + "";
                });

            d3.select("#play-graph svg")
                .datum(playData)
                .call(chart);

            nv.utils.windowResize(function() {
                chart.update();
            });

            // Reset "dy" value
            var noDataElements = document.querySelectorAll('.nv-noData');

            for (var i = 0; i < noDataElements.length; i++) {
                noDataElements[i].setAttribute('dy', 0);
            }

            return chart;
        });
    });
}

function processViewsHistory(entries) {
    var values = entries.map(function(entry) {
        var start = new Date();
        var end = new Date();
        end.setFullYear(entry.year, entry.month - 1);

        var years = start.getFullYear() - end.getFullYear();
        var months = start.getMonth() - end.getMonth();

        var elapsedMonths = years * 12 + months;
        return {
            x: -elapsedMonths,
            y: entry.replay_views
        };
    });

    values = values.reverse();

    return [{
        values: values,
        key: 'Replay Views',
        color: '#f78e25',
        area: true
    }];
}

function loadUserViewsGraph(userId, mode) {
    var url = "/users/" + userId + "/history/views/" + mode;

    performApiRequest("GET", url, null, function(xhr) {
        var entries = JSON.parse(xhr.responseText);
        var viewsData = processViewsHistory(entries);

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .margin({
                    left: 80,
                    bottom: 20,
                    right: 50
                })
                .useInteractiveGuideline(true)
                .transitionDuration(250)
                .interpolate("linear")
                .showLegend(false)
                .showYAxis(true)
                .showXAxis(true);

            chart.xAxis
                .axisLabel("Months")
                .tickFormat(function(month) {
                    if (month % 1 !== 0) return "";
                    if (month == 0) return "This Month";
                    if (month > 0) return (month != 1) ? "In " + month + " months" : "In " + month + " month";
                    return (month != -1) ? (-month + " months ago") : (-month + " month ago");
                });

            chart.yAxis
                .axisLabel("Views")
                .tickFormat(function(views) {
                    return Math.round(views).toString();
                });

            d3.select("#replay-graph svg")
                .datum(viewsData)
                .call(chart);

            nv.utils.windowResize(function() {
                chart.update();
            });

            // Reset "dy" value
            var textElements = document.querySelectorAll('.nv-noData');
            for (var i = 0; i < textElements.length; i++) {
                textElements[i].setAttribute('dy', 0);
            }

            return chart;
        });
    });
}

function updatePlaystyleElement(element) {
    var selected = element.classList.contains('playstyle');
    var url = "/users/" + userId + "/playstyle";

    if (selected) {
        element.classList.remove('playstyle');
        element.classList.add('playstyle-hidden');
        performApiRequest("DELETE", url, {"playstyle": element.id});
    } else {
        element.classList.add('playstyle');
        element.classList.remove('playstyle-hidden');
        performApiRequest("POST", url, {"playstyle": element.id});
    }
}

function addFriend() {
    if (!isLoggedIn())
        return;

    performApiRequest("POST", "/account/friends?id=" + userId, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var friendStatus = document.getElementById('friend-status');
        friendStatus.classList.remove('friend-add');
        friendStatus.classList.add('friend-remove');
        friendStatus.onclick = function() {
            return removeFriend();
        };

        if (data.status === 'mutual')
            friendStatus.innerText = 'Remove Mutual Friend';
        else
            friendStatus.innerText = 'Remove Friend';
    });

    return false;
}

function removeFriend() {
    if (!isLoggedIn())
        return;

    performApiRequest("DELETE", "/account/friends?id=" + userId, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var friendStatus = document.getElementById('friend-status');
        friendStatus.classList.remove('friend-remove');
        friendStatus.classList.add('friend-add');
        friendStatus.onclick = function() {
            return addFriend();
        };

        if (data.status === 'mutual')
            friendStatus.innerText = 'Add Mutual Friend';
        else
            friendStatus.innerText = 'Add Friend';
    });

    return false;
}

function removeFavourite(setId) {
    var url = "/users/" + currentUser + "/favourites/" + setId;

    performApiRequest("DELETE", url, null, function(xhr) {
        var data = JSON.parse(xhr.responseText);
        var favouritesContainer = document.querySelector(".favourites");
        var container = document.getElementById("favourite-" + setId);
        var beatmapsContainer = document.getElementById("beatmaps");

        if (!container)
            return;

        container.style.opacity = 0;

        setTimeout(function() {
            container.remove();

            if (data.length == 0) {
                // User has no favourite beatmaps anymore
                var textElement = document.createElement("p");
                textElement.style.margin = "5px";
                textElement.innerHTML = "This player has no favourite beatmaps :(";
                favouritesContainer.appendChild(textElement);
            }
        }, 350);

        setTimeout(function() {
            slideUp(beatmapsContainer);
            setTimeout(function() { slideDown(beatmapsContainer) }, 150);
        }, 400);
    });

    return false;
}

function deleteBeatmap(setId) {
    var proceed = confirm('Are you sure you want to delete this beatmap?');
    var url = "/users/" + currentUser + "/beatmapsets/" + setId;

    if (!proceed)
        return;

    performApiRequest("DELETE", url, null, function(xhr) {
        window.location.href = "/u/" + currentUser + "#beatmaps";
        window.location.reload();
    }, function(xhr) {
        try {
            var data = JSON.parse(xhr.responseText);
            alert(data.details);
        } catch (e) {
            console.error("Failed to revive beatmap:", e);
            alert("Failed to revive beatmap.");
        }
    });
}

function reviveBeatmap(setId) {
    var url = "/users/" + currentUser + "/beatmapsets/" + setId + "/revive";
    performApiRequest("POST", url, null, function(xhr) {
        window.location.href = "/u/" + currentUser + "#beatmaps";
        window.location.reload();
    }, function(xhr) {
        try {
            var data = JSON.parse(xhr.responseText);
            alert(data.details);
        } catch (e) {
            console.error("Failed to revive beatmap:", e);
            alert("Failed to revive beatmap.");
        }
    });
}

function toggleBeatmapContainer(section) {
    var container = section.querySelector('.profile-beatmaps-container');
    var beatmapsSection = document.getElementById("beatmaps");

    if (container.style.display === 'none') {
        container.style.display = 'block';
        slideDown(beatmapsSection);
    } else {
        container.style.display = 'none';
        beatmapsSection.style.height = getElementHeight(beatmapsSection) + "px";
    }
}

addEvent('DOMContentLoaded', document, function(event) {
    var beatmapContainers = document.getElementsByClassName('profile-beatmaps-container');
    for (var i = 0; i < beatmapContainers.length; i++) {
        beatmapContainers[i].style.display = 'none';
    }

    expandProfileTab(activeTab);
    loadPinnedScores(userId, modeName);
    loadTopPlays(userId, modeName, 5, 0);
    loadLeaderScores(userId, modeName, 5, 0);
    loadRecentPlays(userId, modeName);
    loadMostPlayed(userId, 15, 0);
});