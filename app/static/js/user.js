var activeTab = window.location.hash !== "" ? window.location.hash.replace("#", "") : "general";
var topLeaderOffset = 0;
var topScoreOffset = 0;

function slideDown(elem) {
    elem.style.height = elem.scrollHeight + "px";
}

function slideUp(elem) {
    elem.style.height = "0px";
}

var Mods = {
    NoMod: 0,
    NoFail: 1 << 0,
    Easy: 1 << 1,
    NoVideo: 1 << 2,
    Hidden: 1 << 3,
    HardRock: 1 << 4,
    SuddenDeath: 1 << 5,
    DoubleTime: 1 << 6,
    Relax: 1 << 7,
    HalfTime: 1 << 8,
    Nightcore: 1 << 9,
    Flashlight: 1 << 10,
    Autoplay: 1 << 11,
    SpunOut: 1 << 12,
    Autopilot: 1 << 13,
    Perfect: 1 << 14,
    Key4: 1 << 15,
    Key5: 1 << 16,
    Key6: 1 << 17,
    Key7: 1 << 18,
    Key8: 1 << 19,
    FadeIn: 1 << 20,
    Random: 1 << 21,
    LastMod: 1 << 29,
    KeyMod: (1 << 15) | (1 << 16) | (1 << 17) | (1 << 18) | (1 << 19),
    SpeedMods: (1 << 6) | (1 << 8) | (1 << 9),
    FreeModAllowed: (1 << 0) | (1 << 1) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 10) | (1 << 20) | (1 << 7) | (1 << 13) | (1 << 12) | (1 << 15) | (1 << 16) | (1 << 17) | (1 << 18) | (1 << 19),

    getMembers: function() {
        var memberList = [];
        for (var mod in Mods) {
            if (Mods.hasOwnProperty(mod) && Mods[mod] === (Mods[mod] & this[mod])) {
                memberList.push(mod);
            }
        }
        return memberList;
    },

    getString: function(value) {
        var modMap = {};
        modMap[Mods.NoMod] = "NM";
        modMap[Mods.NoFail] = "NF";
        modMap[Mods.Easy] = "EZ";
        modMap[Mods.Hidden] = "HD";
        modMap[Mods.HardRock] = "HR";
        modMap[Mods.SuddenDeath] = "SD";
        modMap[Mods.DoubleTime] = "DT";
        modMap[Mods.Relax] = "RX";
        modMap[Mods.HalfTime] = "HT";
        modMap[Mods.Nightcore] = "NC";
        modMap[Mods.Flashlight] = "FL";
        modMap[Mods.Autoplay] = "AT";
        modMap[Mods.SpunOut] = "SO";
        modMap[Mods.Autopilot] = "AP";
        modMap[Mods.Perfect] = "PF";
        modMap[Mods.Key4] = "K4";
        modMap[Mods.Key5] = "K5";
        modMap[Mods.Key6] = "K6";
        modMap[Mods.Key7] = "K7";
        modMap[Mods.Key8] = "K8";

        var members = [];
        for (var mod in Mods) {
            if (Mods.hasOwnProperty(mod) && Mods[mod] !== 0 && (value & Mods[mod]) === Mods[mod]) {
                members.push(mod);
            }
        }

        if (members.indexOf("DT") !== -1 && members.indexOf("NC") !== -1) {
            members.splice(members.indexOf("DT"), 1);
        }

        var result = [];
        for (var i = 0; i < members.length; i++) {
            result.push(modMap[Mods[members[i]]]);
        }
        return result.join("");
    }
};

function pinScore(scoreId, userId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/profile/" + userId + "/pinned/add/" + scoreId, true);
    xhr.onload = function() {
        loadPinnedScores(userId, modeName);
    };
    xhr.send();
}

function unpinScore(scoreId, userId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/profile/" + userId + "/pinned/remove/" + scoreId, true);
    xhr.onload = function() {
        loadPinnedScores(userId, modeName);
    };
    xhr.send();
}

function expandProfileTab(id, forceExpand) {
  var tab = document.getElementById(id);
  activeTab = id;

  if (!tab) {
      // Tab can be null sometimes?
      return;
  }

  // Check for 'expanded' class
  if (tab.className.indexOf("expanded") === -1 || forceExpand) {
      tab.className += " expanded";
      tab.style.display = "block";

      if (tab.style.height === "0px") {
          slideDown(tab);
      }

      if (forceExpand) {
          window.location.hash = "#" + activeTab;
      }
  } else {
      slideUp(tab);
      tab.className = tab.className.replace(/(?:^|\s)expanded(?!\S)/, '');
  }

  if (activeTab === 'general') {
      loadUserPerformanceGraph(userId, modeName);
  } else {
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
  beatmapInfo.textContent = score.beatmap.beatmapset.artist + " - " + score.beatmap.beatmapset.title + " [" + score.beatmap.version + "]";

  var modsText = document.createElement("b");
  if (score.mods > 0) {
    modsText.textContent = "+" + Mods.getString(score.mods);
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

  var dateText = document.createElement("time");
  dateText.setAttribute("datetime", scoreDateString);
  dateText.textContent = score.submitted_at; 
  dateText.className = "timeago";

  var rightColumn = document.createElement("td");
  rightColumn.className = 'score-right';

  var ppText = document.createElement("b");
  ppText.textContent = (score.pp.toFixed(0) + "pp");

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

  var dateDiv = document.createElement("div");
  dateDiv.appendChild(dateText);

  if (currentUser === userId) {
    var pinIcon = document.createElement("i");
    pinIcon.className = "fa-regular fa-star score-pin-" + score.id;

    if (!score.pinned) {
      pinIcon.className += " score-pin-icon"; // Append className
      pinIcon.title = "Pin Score";
      pinIcon.onclick = function () {
        var icons = document.querySelectorAll(".score-pin-" + score.id);
        for (var j = 0; j < icons.length; j++) {
          icons[j].classList.remove("score-pin-icon");
          icons[j].classList.add("score-pinned-icon");
          icons[j].title = "Unpin Score";
        }
        pinScore(score.id, userId);
        pinIcon.onclick = function () {
          unpinScore(score.id, userId);
          pinIcon.classList.remove("score-pinned-icon");
          pinIcon.classList.add("score-pin-icon");
          pinIcon.title = "Pin Score";
        };
      };
    } else {
      pinIcon.className += " score-pinned-icon"; // Append className
      pinIcon.title = "Unpin Score";
      pinIcon.onclick = function () {
        var icons = document.querySelectorAll(".score-pin-" + score.id);
        for (var j = 0; j < icons.length; j++) {
          icons[j].classList.remove("score-pinned-icon");
          icons[j].classList.add("score-pin-icon");
          icons[j].title = "Pin Score";
        }
        unpinScore(score.id, userId);
        pinIcon.onclick = function () {
          pinScore(score.id, userId);
          pinIcon.classList.remove("score-pin-icon");
          pinIcon.classList.add("score-pinned-icon");
          pinIcon.title = "Unpin Score";
        };
      };
    }

    iconContainer.appendChild(pinIcon);
  }
  else {
    var replayLink = document.createElement("a");
    replayLink.href = "/scores/" + score.id + "/download";
    replayLink.className = "score-replay";
    replayLink.title = "Download Replay";
    replayLink.target = "_blank";

    var replayIcon = document.createElement("i");
    replayIcon.className = "fa-regular fa-star";
    replayLink.appendChild(replayIcon);

    iconContainer.appendChild(replayLink);
  }

  ppWeight.appendChild(iconContainer);
  leftColumn.appendChild(scoreInfoDiv);
  leftColumn.appendChild(dateDiv);
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
  var url = "/api/profile/" + userId + "/pinned/" + mode;
  var scoreContainer = document.getElementById("pinned-scores");

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
          console.error("Error loading pinned scores:", xhr.status);
          var errorText = document.createElement("p");
          errorText.textContent = "Failed to load pinned scores.";
          errorText.classList.add("score");
          scoreContainer.appendChild(errorText);
          
          var loadingText = document.getElementById("pinned-scores-loading");
          if (loadingText) {
              loadingText.parentElement.classList.remove("score");
              loadingText.remove();
          }
          return;
      }

      var data = JSON.parse(xhr.responseText);
      var loadingText = document.getElementById("pinned-scores-loading");
      var scores = data.scores;

      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }

      // Reset container
      scoreContainer.innerHTML = "<h2>Pinned Scores</h2>";

      if (scores.length <= 0) {
          scoreContainer.appendChild(
              document.createTextNode("This player has not pinned any scores yet :(")
          );
          return;
      }

      for (var index = 0; index < scores.length; index++) {
          var score = scores[index];
          var scoreDiv = createScoreElement(score, index, "pinned");
          scoreContainer.appendChild(scoreDiv);
      }

      // Render timeago elements
      $(".timeago").timeago();

      slideDown(document.getElementById("leader"));
  };

  xhr.onerror = function() {
      console.error("Error loading pinned scores:", xhr.status);

      var errorText = document.createElement("p");
      errorText.textContent = "Failed to load pinned scores.";
      errorText.classList.add("score");
      scoreContainer.appendChild(errorText);

      var loadingText = document.getElementById("pinned-scores-loading");
      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }
  };

  xhr.send();
}

function loadTopPlays(userId, mode, limit, offset) {
  var url = "/api/profile/" + userId + "/top/" + mode + "?limit=" + limit + "&offset=" + offset;
  var scoreContainer = document.getElementById("top-scores");

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status < 200 || xhr.status >= 300) {
          console.error(xhr.status);
          var errorText = document.createElement("p");
          errorText.textContent = "Failed to load top plays.";
          errorText.classList.add("score");
          scoreContainer.appendChild(errorText);
          var loadingText = document.getElementById("top-scores-loading");

          if (loadingText) {
              loadingText.parentElement.classList.remove("score");
              loadingText.remove();
          }
          return;
      }

      var data = JSON.parse(xhr.responseText);
      var loadingText = document.getElementById("top-scores-loading");
      var scores = data.scores;

      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }

      if (scores.length <= 0 && offset <= 0) {
          var noScoresText = document.createElement("p");
          noScoresText.textContent = "No awesome performance records yet :(";
          scoreContainer.appendChild(noScoresText);
          return;
      }

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
      $(".timeago").timeago();

      if (scores.length >= limit) {
          // Create show more text
          var showMoreText = document.createElement("b");
          showMoreText.textContent = "Show me more!";

          // Add onclick event
          var showMoreHref = document.createElement("a");
          showMoreHref.href = "#score-top-" + scores.length;
          showMoreHref.id = "show-more-top";
          showMoreHref.appendChild(showMoreText);
          showMoreHref.onclick = function() {
              var loadingText = document.createElement("p");
              loadingText.textContent = "Loading...";
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
  };

  xhr.onerror = function() {
      console.error("Error loading top scores:", error);
      var errorText = document.createElement("p");
      errorText.textContent = "Failed to load top plays.";
      errorText.classList.add("score");
      scoreContainer.appendChild(errorText);

      var loadingText = document.getElementById("top-scores-loading");

      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }
  };

  xhr.send();

  return false;
}

function loadLeaderScores(userId, mode, limit, offset) {
  var url = "/api/profile/" + userId + "/first/" + mode + "?limit=" + limit + "&offset=" + offset;
  var scoreContainer = document.getElementById("leader-scores");

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
          console.error("Error loading leader scores:", xhr.status);
          var errorText = document.createElement("p");
          errorText.textContent = "Failed to load first place ranks.";
          errorText.classList.add("score");
          scoreContainer.appendChild(errorText);
          var loadingText = document.getElementById("leader-scores-loading");
          if (loadingText) {
              loadingText.parentElement.classList.remove("score");
              loadingText.remove();
          }
          return;
      }

      var data = JSON.parse(xhr.responseText);
      var loadingText = document.getElementById("leader-scores-loading");
      var scores = data.scores;

      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }

      if (scores.length <= 0) {
          var noScoresText = document.createElement("p");
          noScoresText.textContent = "No first place records currently :(";
          scoreContainer.appendChild(noScoresText);
          return;
      }

      for (var i = 0; i < scores.length; i++) {
          var scoreDiv = createScoreElement(scores[i], i, "leader");
          scoreContainer.appendChild(scoreDiv);
      }
      topLeaderOffset += scores.length;

      // Render timeago elements
      $(".timeago").timeago();

      if (scores.length >= limit) {
          var showMoreText = document.createElement("b");
          showMoreText.textContent = "Show me more!";

          // Add onclick event
          var showMoreHref = document.createElement("a");
          showMoreHref.href = "#score-leader-" + scores.length;
          showMoreHref.id = "show-more-leader";
          showMoreHref.appendChild(showMoreText);
          showMoreHref.onclick = function() {
              var loadingText = document.createElement("p");
              loadingText.textContent = "Loading...";
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
  };
  xhr.onerror = function() {
      console.error("Error loading leader scores:", xhr.status);
      var errorText = document.createElement("p");
      errorText.textContent = "Failed to load first place ranks.";
      errorText.classList.add("score");
      scoreContainer.appendChild(errorText);

      var loadingText = document.getElementById("leader-scores-loading");
      if (loadingText) {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
      }
  };
  xhr.send();

  return false;
}

function loadMostPlayed(userId, limit, offset) {
  var loadingText = document.getElementById("plays-loading");

  if (!loadingText)
      return;

  var url = "/api/profile/" + userId + "/plays?limit=" + limit + "&offset=" + offset;
  var playsContainer = document.getElementById("plays-container");

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) 
          throw new Error(xhr.status);
      
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
          beatmapLink.textContent = item.beatmap.beatmapset.artist + " - " + item.beatmap.beatmapset.title + " [" + item.beatmap.version + "]";
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
  };
  xhr.onerror = function() {
      console.error("Request failed");
  };
  xhr.send();

  loadingText.remove();
}

function loadRecentPlays(userId, mode) {
  var loadingText = document.getElementById("recent-loading");

  if (!loadingText)
      return;

  var url = "/api/profile/" + userId + "/recent/" + mode;
  var playsContainer = document.getElementById("recent-container");

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
          throw new Error(xhr.status);
      }
      var scores = JSON.parse(xhr.responseText);
      if (scores.length <= 0) {
          playsContainer.appendChild(
              document.createTextNode("No recent scores set by this player :(")
          );
          return;
      }

      // TODO: I would like to refactor this in the future...

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
          dateText.setAttribute("datetime", scoreDateString);
          dateText.textContent = score.submitted_at;
          dateText.className += " timeago";

          var beatmapLink = document.createElement("a");
          beatmapLink.textContent = score.beatmap.beatmapset.artist + " - " + score.beatmap.beatmapset.title + " [" + score.beatmap.version + "]";
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
      $(".timeago").timeago();

      // Slide down tab
      slideDown(document.getElementById("history"));
  };
  xhr.onerror = function() {
      console.error("Request failed");
  };
  xhr.send();

  loadingText.parentNode.removeChild(loadingText);
}

function processRankHistory(entries) {
  var globalRankValues = entries.map(function(entry) {
      var difference = (Date.now() - Date.parse(entry.time));
      var elapsedDays = Math.ceil(difference / (1000 * 3600 * 24));
      return {x: -elapsedDays, y: -entry.global_rank};
  });

  var scoreRankValues = entries.map(function(entry) {
      var difference = (Date.now() - Date.parse(entry.time));
      var elapsedDays = Math.ceil(difference / (1000 * 3600 * 24));
      return {x: -elapsedDays, y: -entry.score_rank};
  });

  var countryRankValues = entries.map(function(entry) {
      var difference = (Date.now() - Date.parse(entry.time));
      var elapsedDays = Math.ceil(difference / (1000 * 3600 * 24));
      return {x: -elapsedDays, y: -entry.country_rank};
  });

  var ppv1RankValues = entries.map(function(entry) {
      var difference = (Date.now() - Date.parse(entry.time));
      var elapsedDays = Math.ceil(difference / (1000 * 3600 * 24));
      return {x: -elapsedDays, y: -entry.ppv1_rank};
  });

  if (entries.length > 0) {
      countryRankValues.unshift({x: 0, y: -countryRank});
      globalRankValues.unshift({x: 0, y: -globalRank});
      scoreRankValues.unshift({x: 0, y: -scoreRank});
      ppv1RankValues.unshift({x: 0, y: -ppv1Rank});
  }

  ppv1RankValues = ppv1RankValues.filter(function(e) { return e.y != 0; });
  scoreRankValues = scoreRankValues.filter(function(e) { return e.y != 0; });
  globalRankValues = globalRankValues.filter(function(e) { return e.y != 0; });
  countryRankValues = countryRankValues.filter(function(e) { return e.y != 0; });

  ppv1RankValues = ppv1RankValues.reverse();
  scoreRankValues = scoreRankValues.reverse();
  globalRankValues = globalRankValues.reverse();
  countryRankValues = countryRankValues.reverse();

  return [
      {
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

function loadUserPerformanceGraph(userId, mode)
{
    var url = '/api/profile/' + userId + '/history/rank/' + mode;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return;

        if (xhr.status >= 200 && xhr.status < 300) {
            var entries = JSON.parse(xhr.responseText);
            var rankData = processRankHistory(entries);

            nv.addGraph(function() {
                var chart = nv.models.lineChart()
                    .margin({left: 80, bottom: 20, right: 50})
                    .useInteractiveGuideline(true)
                    .transitionDuration(250)
                    .interpolate("step")
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

                rankData.forEach(function(axis) {
                    axis.values.forEach(function(value) {
                        ranks.push(-value.y);
                    });
                });

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
                // chart.forceX([-90, 0]);
                chart.forceY([-relativeMinRank - 1, -relativeMaxRank]);

                // Only display certain tick values
                chart.xAxis.tickValues([-90, -60, -30, 0]);
                chart.yAxis.tickValues([-relativeMaxRank, -betweenRank, -relativeMinRank]);

                d3.select("#rank-graph svg")
                    .datum(rankData)
                    .call(chart);

                nv.utils.windowResize(function() { chart.update(); });

                // Reset "dy" value
                document.querySelectorAll('.nv-noData')
                    .forEach(function(textElement) {
                        textElement.setAttribute('dy', 0);
                    });

                return chart;
            });
        } else {
            console.error(xhr.status);
        }
    };
    
    xhr.send();
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
      values.push({ x: -elapsedMonths, y: entry.plays });
  }

  values.reverse();

  return [
      {
          values: values,
          key: 'Plays',
          color: '#f5f242',
          area: true
      }
  ];
}

function loadUserPlaysGraph(userId, mode) {
  var url = "/api/profile/" + userId + "/history/plays/" + mode;

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
          throw new Error(xhr.status);
      }
      var entries = JSON.parse(xhr.responseText);
      var playData = processPlayHistory(entries);

      nv.addGraph(function() {
          var chart = nv.models.lineChart()
              .margin({left: 80, bottom: 20, right: 50})
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
          document.querySelectorAll('.nv-noData')
              .forEach(function(textElement) {
                  textElement.setAttribute('dy', 0);
              });

          return chart;
      });
  };
  
  xhr.onerror = function() {
      console.error("Request failed");
  };

  xhr.send();
}

function processViewsHistory(entries) {
  var values = entries.map(function(entry) {
      var start = new Date();
      var end = new Date();
      end.setFullYear(entry.year, entry.month - 1);

      var years = start.getFullYear() - end.getFullYear();
      var months = start.getMonth() - end.getMonth();

      var elapsedMonths = years * 12 + months;
      return { x: -elapsedMonths, y: entry.replay_views };
  });

  values = values.reverse();

  return [
      {
          values: values,
          key: 'Replay Views',
          color: '#f78e25',
          area: true
      }
  ];
}

function loadUserViewsGraph(userId, mode) {
  var url = "/api/profile/" + userId + "/history/views/" + mode;

  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
          console.error(xhr.status);
          return;
      }

      var entries = JSON.parse(xhr.responseText);
      var viewsData = processViewsHistory(entries);

      nv.addGraph(function() {
          var chart = nv.models.lineChart()
              .margin({ left: 80, bottom: 20, right: 50 })
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

          nv.utils.windowResize(function() { chart.update(); });

          // Reset "dy" value
          var textElements = document.querySelectorAll('.nv-noData');
          for (var i = 0; i < textElements.length; i++) {
              textElements[i].setAttribute('dy', 0);
          }

          return chart;
      });
  };
  xhr.onerror = function() {
      console.error("Request failed");
  };
  xhr.send();
}

function updatePlaystyleElement(element) {
  var selected = element.classList.contains('playstyle');

  if (selected) {
      element.classList.remove('playstyle');
      element.classList.add('playstyle-hidden');
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/api/profile/playstyle/remove?type=" + element.id, true);
      xhr.send();
  } else {
      element.classList.add('playstyle');
      element.classList.remove('playstyle-hidden');
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/api/profile/playstyle/add?type=" + element.id, true);
      xhr.send();
  }
}

function addFriend() {
  if (!isLoggedIn())
      return;

  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api/profile/friends/add?id=" + userId, true);
  xhr.onload = function() {
      if (xhr.status < 200 || xhr.status >= 300) {
          console.error(xhr.status + ': "' + xhr.statusText + '"');
          return;
      }
      var data = JSON.parse(xhr.responseText);
      var friendStatus = document.getElementById('friend-status');
      friendStatus.classList.remove('friend-add');
      friendStatus.classList.add('friend-remove');
      friendStatus.onclick = function() { return removeFriend(); };

      if (data.status === 'mutual')
          friendStatus.innerText = 'Remove Mutual Friend';
      else
          friendStatus.innerText = 'Remove Friend';
  };
  xhr.onerror = function() {
      console.error("Request failed");
  };
  xhr.send();

  return false;
}

function removeFriend() {
  if (!isLoggedIn())
      return;

  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api/profile/friends/remove?id=" + userId, true);
  xhr.onload = function() {
      if (xhr.status < 200 || xhr.status >= 300) {
          console.error(xhr.status + ': "' + xhr.statusText + '"');
          return;
      }
      var data = JSON.parse(xhr.responseText);
      var friendStatus = document.getElementById('friend-status');
      friendStatus.classList.remove('friend-remove');
      friendStatus.classList.add('friend-add');
      friendStatus.onclick = function() { return addFriend(); };

      if (data.status === 'mutual')
          friendStatus.innerText = 'Add Mutual Friend';
      else
          friendStatus.innerText = 'Add Friend';
  };
  xhr.onerror = function() {
      console.error("Request failed");
  };
  xhr.send();

  return false;
}

function removeFavourite(setId) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api/profile/" + currentUser + "/favourites/delete?set_id=" + setId, true);
  xhr.onload = function() {
    if (xhr.status < 200 || xhr.status >= 300) {
      console.error(xhr.status + ': "' + xhr.statusText + '"');
      return;
    }
    
    var data = JSON.parse(xhr.responseText);
    var favouritesContainer = document.querySelector(".favourites");
    var container = document.getElementById("favourite-" + setId);
    var beatmapsContainer = document.getElementById("beatmaps");

    console.log(beatmapsContainer.scrollHeight);

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

      setTimeout(function() {
        slideDown(beatmapsContainer);
      }, 150);
    }, 400);
  };
  
  xhr.onerror = function() {
    console.error("An error occurred during the request");
  };

  xhr.send();

  return false;
}

function deleteBeatmap(setId) {
  var proceed = confirm('Are you sure you want to delete this beatmap?');

  if (!proceed)
    return;

  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api/profile/" + currentUser + "/beatmaps/delete?set_id=" + setId, true);
  xhr.onload = function() {
    if (xhr.status !== 200) {
      console.error("Error: " + xhr.status);
      return;
    }

    var data = JSON.parse(xhr.responseText);
    if (data.error) {
      alert(data.details);
      return;
    }

    window.location.href = "/u/" + currentUser + "#beatmaps";
    window.location.reload();
  };
  xhr.onerror = function() {
    console.error(xhr.statusText);
  };
  xhr.send();
}

function reviveBeatmap(setId) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api/profile/" + currentUser + "/beatmaps/revive?set_id=" + setId, true);
  xhr.onload = function() {
      if (xhr.status !== 200) {
        return;
      }

      var data = JSON.parse(xhr.responseText);
      if (data.error) {
          alert(data.details);
          return;
      }

      window.location.href = "/u/" + currentUser + "#beatmaps";
      window.location.reload();
  };
  xhr.onerror = function() {
      console.error(xhr.statusText);
  };
  xhr.send();
}

window.addEventListener('load', function() {
    expandProfileTab(activeTab);
    loadPinnedScores(userId, modeName);
    loadTopPlays(userId, modeName, 5, 0);
    loadLeaderScores(userId, modeName, 5, 0);
    loadRecentPlays(userId, modeName);
    loadMostPlayed(userId, 15, 0);
});