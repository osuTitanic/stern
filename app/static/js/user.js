var activeTab = window.location.hash != "" ? window.location.hash.replace("#","") : "general";
var topScoreOffset = 0;

const slideDown = elem => elem.style.height = `${elem.scrollHeight}px`;
const slideUp = elem => elem.style.height = "0px";

const Mods = {
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
    KeyMod: 1 << 15 | 1 << 16 | 1 << 17 | 1 << 18 | 1 << 19,
    SpeedMods: 1 << 6 | 1 << 8 | 1 << 9,
    FreeModAllowed: 1 << 0 | 1 << 1 | 1 << 3 | 1 << 4 | 1 << 5 | 1 << 10 | 1 << 20 | 1 << 7 | 1 << 13 | 1 << 12 | 1 << 15 | 1 << 16 | 1 << 17 | 1 << 18 | 1 << 19,

    getMembers: function() {
      let memberList = [];
      for (const mod in Mods) {
        if (Mods[mod] === (Mods[mod] & this[mod])) {
          memberList.push(mod);
        }
      }
      return memberList;
    },

    getString: function(value) {
      const modMap = {
        [Mods.NoMod]: "NM",
        [Mods.NoFail]: "NF",
        [Mods.Easy]: "EZ",
        [Mods.Hidden]: "HD",
        [Mods.HardRock]: "HR",
        [Mods.SuddenDeath]: "SD",
        [Mods.DoubleTime]: "DT",
        [Mods.Relax]: "RX",
        [Mods.HalfTime]: "HT",
        [Mods.Nightcore]: "NC",
        [Mods.Flashlight]: "FL",
        [Mods.Autoplay]: "AT",
        [Mods.SpunOut]: "SO",
        [Mods.Autopilot]: "AP",
        [Mods.Perfect]: "PF",
        [Mods.Key4]: "K4",
        [Mods.Key5]: "K5",
        [Mods.Key6]: "K6",
        [Mods.Key7]: "K7",
        [Mods.Key8]: "K8",
      };

      const members = [];
      for (const mod in Mods) {
        if (Mods[mod] !== 0 && (value & Mods[mod]) === Mods[mod]) {
          members.push(mod);
        }
      }

      return members.map(mod => modMap[Mods[mod]]).join("");
    }
};

function expandProfileTab(id, forceExpand)
{
    var tab = document.getElementById(id);
    activeTab = id;

    if (!tab)
      // Tab can be null sometimes?
      return

    if (!tab.classList.contains("expanded") || forceExpand)
    {
        tab.classList.add("expanded");
        tab.style.display = "block";

        if (tab.style.height == "0px")
            slideDown(tab);

        if (forceExpand)
            window.location.hash = "#" + activeTab;
    }
    else
    {
        slideUp(tab);
        tab.classList.remove("expanded");
        tab.addEventListener("transitionend", () => {
            tab.style.display = "none";
        }, { once: true })
    }
}

function expandRecentActivity()
{
    document.getElementById("profile-recent-preview").style.display = "none";
    document.getElementById("profile-recent-full").style.display = "block";
    slideDown(document.getElementById("general"));
}

function createScoreElement(score, index, type)
{
  const scoreDiv = document.createElement("div");
  scoreDiv.id = `score-${type}-${index}`;
  scoreDiv.classList.add("score");

  const scoreTable = document.createElement("table");
  const tableBody = document.createElement("tbody");
  const tableRow = document.createElement("tr");

  const leftColumn = document.createElement("td");
  leftColumn.classList.add('score-left');

  const scoreGrade = document.createElement("img");
  scoreGrade.src = `/images/grades/${score.grade}_small.png`
  scoreGrade.loading = "lazy";

  const beatmapInfo = document.createElement("a");
  beatmapInfo.href = `/b/${score.beatmap.id}?mode=${score.mode}`;
  beatmapInfo.textContent = `${score.beatmap.beatmapset.artist} - ${score.beatmap.beatmapset.title} [${score.beatmap.version}]`;

  const modsText = document.createElement("b");

  if (score.mods > 0)
    modsText.textContent = `+${Mods.getString(score.mods)}`;

  const scoreInfo = document.createElement("b");
  scoreInfo.appendChild(beatmapInfo);
  scoreInfo.appendChild(modsText);

  const accuracyText = document.createTextNode(`(${(score.acc * 100).toFixed(2)}%)`);

  // Parse date to a format that timeago can understand
  const scoreDate = new Date(score.submitted_at);
  const scoreDateString = scoreDate.toLocaleDateString(
    "en-us", {
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short",
    }
  );

  const dateText = document.createElement("time");
  dateText.setAttribute("datetime", scoreDateString);
  dateText.textContent = score.submitted_at;
  dateText.classList.add("timeago");

  const rightColumn = document.createElement("td");
  rightColumn.classList.add('score-right');

  const ppText = document.createElement("b");
  ppText.textContent = `${score.pp.toFixed(0)}pp`;

  const ppDisplay = document.createElement("div");
  ppDisplay.classList.add("pp-display");
  ppDisplay.appendChild(ppText);

  const ppWeightPercent = document.createElement("b");
  ppWeightPercent.textContent = `${((0.95**(index + topScoreOffset)) * 100).toFixed(0)}%`;

  const ppWeight = document.createElement("div");
  ppWeight.classList.add("pp-display-weight");
  ppWeight.appendChild(document.createTextNode("weighted "));
  ppWeight.appendChild(ppWeightPercent);
  ppWeight.appendChild(document.createTextNode(` (${(score.pp * (0.95**(index + topScoreOffset))).toFixed(0)}pp)`));

  const scoreInfoDiv = document.createElement("div");
  scoreInfoDiv.appendChild(scoreGrade);
  scoreInfoDiv.appendChild(scoreInfo);
  scoreInfoDiv.appendChild(accuracyText);

  const dateDiv = document.createElement("div");
  dateDiv.appendChild(dateText);

  // TODO: Create replay download button

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

function loadTopPlays(userId, mode, limit, offset)
{
    var url = `/api/profile/${userId}/top/${mode}?limit=${limit}&offset=${offset}`;
    var scoreContainer = document.getElementById("top-scores");

    fetch(url)
      .then(response => {
        if (!response.ok) {
            const errorText = document.createElement("p");
            errorText.textContent = "Failed to load top plays.";
            scoreContainer.appendChild(errorText);

            var loadingText = document.getElementById("top-scores-loading");

            if (loadingText)
              loadingText.remove();

            throw new Error(`${response.status}`);
          }
          return response.json();
      })
      .then(scores => {
        var loadingText = document.getElementById("top-scores-loading");

        if (loadingText)
        {
          loadingText.parentElement.classList.remove("score");
          loadingText.remove();
        }

        if (scores.length <= 0)
        {
          var noScoresText = document.createElement("p")
          noScoresText.textContent = "No awesome performance records yet :(. ";
          noScoresText.style.fontSize = "80%";
          scoreContainer.appendChild(noScoresText);
          return;
        }

        for (const [index, score] of scores.entries()) {
            const scoreDiv = createScoreElement(score, index, "top");
            scoreContainer.appendChild(scoreDiv);
        }
        topScoreOffset += scores.length;

        // Render timeago elements
        $(".timeago").timeago();

        if (scores.length >= limit)
        {
            // Create show more text
            const showMoreText = document.createElement("b");
            showMoreText.textContent = "Show me more!";

            // Add onclick event
            const showMoreHref = document.createElement("a");
            showMoreHref.href = `#score-top-${scores.length}`;
            showMoreHref.id = "show-more-top";
            showMoreHref.appendChild(showMoreText);
            showMoreHref.onclick = () => {
                const loadingText = document.createElement("p");
                loadingText.textContent = "Loading...";
                loadingText.id = "top-scores-loading";

                const showMore = document.getElementById("show-more-top");
                showMore.parentElement.appendChild(loadingText);
                showMore.remove();

                loadTopPlays(userId, modeName, 50, topScoreOffset);
            }

            // Create wrapper that contains styling
            const showMore = document.createElement("div");
            showMore.classList.add("score", "show-more");
            showMore.appendChild(showMoreHref);

            // Append show more text to container
            scoreContainer.appendChild(showMore);
        }

        slideDown(document.getElementById("leader"));
      })
      .catch(error => {
        console.error("Error loading top scores:", error);

        var loadingText = document.getElementById("top-scores-loading");

        if (loadingText)
          loadingText.remove();
      });

    return false;
}

function loadLeaderScores(userId, mode, limit, offset)
{
  var url = `/api/profile/${userId}/first/${mode}?limit=${limit}&offset=${offset}`;
  var scoreContainer = document.getElementById("leader-scores");

  fetch(url)
    .then(response => {
      if (!response.ok) {
          const errorText = document.createElement("p");
          errorText.textContent = "Failed to load first place ranks.";
          scoreContainer.appendChild(errorText);

          var loadingText = document.getElementById("leader-scores-loading");

          if (loadingText)
            loadingText.remove();

          throw new Error(`${response.status}`);
        }
        return response.json();
    })
    .then(scores => {
      var loadingText = document.getElementById("leader-scores-loading");

      if (loadingText)
      {
        loadingText.parentElement.classList.remove("score");
        loadingText.remove();
      }

      if (scores.length <= 0)
      {
        var noScoresText = document.createElement("p")
        noScoresText.textContent = "No first place records currently :(. ";
        noScoresText.style.fontSize = "80%";
        scoreContainer.appendChild(noScoresText);
        return;
      }

      for (const [index, score] of scores.entries()) {
        const scoreDiv = createScoreElement(score, index, "leader");
        scoreContainer.appendChild(scoreDiv);
      }
      topScoreOffset += scores.length;

      // Render timeago elements
      $(".timeago").timeago();

      if (scores.length >= limit)
      {
          // Create show more text
          const showMoreText = document.createElement("b");
          showMoreText.textContent = "Show me more!";

          // Add onclick event
          const showMoreHref = document.createElement("a");
          showMoreHref.href = `#score-leader-${scores.length}`;
          showMoreHref.id = "show-more-leader";
          showMoreHref.appendChild(showMoreText);
          showMoreHref.onclick = () => {
              const loadingText = document.createElement("p");
              loadingText.textContent = "Loading...";
              loadingText.id = "leader-scores-loading";

              const showMore = document.getElementById("show-more-leader");
              showMore.parentElement.appendChild(loadingText);
              showMore.remove();

              loadLeaderScores(userId, modeName, 50, topScoreOffset);
          }

          // Create wrapper that contains styling
          const showMore = document.createElement("div");
          showMore.classList.add("score", "show-more");
          showMore.appendChild(showMoreHref);

          // Append show more text to container
          scoreContainer.appendChild(showMore);
      }

      slideDown(document.getElementById("leader"));
    })
    .catch(error => {
      console.error("Error loading leader scores:", error);

      var loadingText = document.getElementById("leader-scores-loading");

      if (loadingText)
        loadingText.remove();
    });

  return false;
}

function onLoad()
{
    expandProfileTab(activeTab);
    loadTopPlays(userId, modeName, 5, 0);
    loadLeaderScores(userId, modeName, 5, 0);
}