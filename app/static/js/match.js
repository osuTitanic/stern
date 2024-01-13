
const matchId = window.location.pathname.split("/")[2];
const refreshRate = 8000;

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
      if (value === 0) return "NM";

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

const Mode = {
    0: "osu!",
    1: "Taiko",
    2: "Catch the Beat",
    3: "osu!Mania"
};

const ScoringType = {
    0: "Score",
    1: "Accuracy",
    2: "Combo"
};

const TeamType = {
    0: "Head to Head",
    1: "Tag Co-op",
    2: "Team VS",
    3: "Tag Team VS"
};

const Team = {
    0: "None",
    1: "Blue",
    2: "Red"
};

function generateResultsTable(results, matchMods=0)
{
    const table = document.createElement("table");
    const headerWrapper = document.createElement("thead");
    const header = document.createElement("tr");

    const headerPlace = document.createElement("th");
    headerPlace.style.width = "25px";
    const headerPlayer = document.createElement("th");
    headerPlayer.innerHTML = "Player";
    const headerScore = document.createElement("th");
    headerScore.innerHTML = "Score";
    const headerAccuracy = document.createElement("th");
    headerAccuracy.innerHTML = "Accuracy";
    const headerCombo = document.createElement("th");
    headerCombo.innerHTML = "Combo";
    const headerMods = document.createElement("th");
    headerMods.innerHTML = "Mods";
    const c300 = document.createElement("th");
    c300.innerHTML = "300s";
    const c100 = document.createElement("th");
    c100.innerHTML = "100s";
    const c50 = document.createElement("th");
    c50.innerHTML = "50s";
    const cMiss = document.createElement("th");
    cMiss.innerHTML = "Misses";

    header.appendChild(headerPlace);
    header.appendChild(headerPlayer);
    header.appendChild(headerScore);
    header.appendChild(headerAccuracy);
    header.appendChild(headerCombo);
    header.appendChild(headerMods);
    header.appendChild(c300);
    header.appendChild(c100);
    header.appendChild(c50);
    header.appendChild(cMiss);
    headerWrapper.appendChild(header);
    table.appendChild(headerWrapper);

    const tableBody = document.createElement("tbody");

    results.forEach(result => {
        const row = document.createElement("tr");

        if (result.score.failed)
            row.classList.add("fail");

        if (results.indexOf(result) % 2 == 0)
            row.classList.add("light-row");
        else
            row.classList.add("dark-row");

        const place = document.createElement("td");
        place.innerHTML = result.place;

        if (result.player.team != 0)
            place.classList.add(
                result.player.team == 1 ? "team-blue" : "team-red"
            );

        const playerLink = document.createElement("a");
        playerLink.innerHTML = result.player.name;
        playerLink.href = `/u/${result.player.id}`;

        const playerFlag = document.createElement("img");
        playerFlag.src = `/images/flags/${result.player.country.toLowerCase()}.gif`;
        playerFlag.classList.add("flag");

        const player = document.createElement("td");
        player.appendChild(playerFlag);
        player.appendChild(playerLink);

        const score = document.createElement("td");
        score.innerHTML = result.score.score.toLocaleString();

        if (result.score.failed)
        {
            const failed = document.createElement("span");
            failed.style.color = "#ff0000";
            failed.innerHTML = " FAIL";
            score.style.fontWeight = "bold";
            score.appendChild(failed);
        }

        const accuracy = document.createElement("td");
        accuracy.innerHTML = `${result.score.accuracy}%`;

        const combo = document.createElement("td");
        combo.innerHTML = `${result.score.max_combo}`;

        const mods = document.createElement("td");
        mods.innerHTML = Mods.getString(result.player.mods + matchMods);

        const c300 = document.createElement("td");
        c300.innerHTML = result.score.c300.toLocaleString();

        const c100 = document.createElement("td");
        c100.innerHTML = result.score.c100.toLocaleString();

        const c50 = document.createElement("td");
        c50.innerHTML = result.score.c50.toLocaleString();

        const cMiss = document.createElement("td");
        cMiss.innerHTML = result.score.cMiss.toLocaleString();

        row.appendChild(place);
        row.appendChild(player);
        row.appendChild(score);
        row.appendChild(accuracy);
        row.appendChild(combo);
        row.appendChild(mods);
        row.appendChild(c300);
        row.appendChild(c100);
        row.appendChild(c50);
        row.appendChild(cMiss);
        tableBody.appendChild(row);
    });

    table.appendChild(tableBody);

    return table;
}

function getTeamWinner(results, condition)
{
    var teamResults = document.createElement("div");
    teamResults.classList.add("team-results");

    switch (condition)
    {
        case 0:
            // Score
            var blueScore = 0;
            var redScore = 0;

            results.forEach(result => {
                if (result.player.team == 1)
                    blueScore += result.score.score;
                else if (result.player.team == 2)
                    redScore += result.score.score;
            });

            var teamBlue = document.createElement("span");
            teamBlue.style.color = "#0000ff";
            teamBlue.innerHTML = `${blueScore.toLocaleString()}`;

            var teamRed = document.createElement("span");
            teamRed.style.color = "#ff0000";
            teamRed.innerHTML = `${redScore.toLocaleString()}`;

            teamResults.appendChild(teamBlue);
            teamResults.appendChild(document.createTextNode(" vs. "));
            teamResults.appendChild(teamRed);

            var scoreDifference = Math.abs(blueScore - redScore);
            var winner = document.createElement("span");
            winner.classList.add("winner");
            winner.style.fontWeight = "bold";

            if (blueScore > redScore)
            {
                winner.style.color = "#0000ff";
                winner.innerHTML = "Blue";
            }
            else if (redScore > blueScore)
            {
                winner.style.color = "#ff0000";
                winner.innerHTML = "Red";
            }
            else
            {
                winner.style.color = "#000000";
                winner.innerHTML = "Draw";
            }

            teamResults.appendChild(document.createElement("br"));
            teamResults.appendChild(winner);
            teamResults.appendChild(document.createTextNode(" wins by "));
            teamResults.appendChild(document.createTextNode(scoreDifference.toLocaleString()));
            teamResults.appendChild(document.createTextNode(" points!"));
            return teamResults;

        case 1:
            // Average Accuracy
            var blueAccs = [];
            var redAccs = [];

            results.forEach(result => {
                if (result.player.team == 1)
                    blueAccs.push(result.score.accuracy);
                else if (result.player.team == 2)
                    redAccs.push(result.score.accuracy);
            });

            var blueAcc = blueAccs.reduce((a, b) => a + b, 0) / blueAccs.length || 0;
            var redAcc = redAccs.reduce((a, b) => a + b, 0) / redAccs.length || 0;

            var teamBlue = document.createElement("span");
            teamBlue.style.color = "#0000ff";
            teamBlue.innerHTML = `${blueAcc.toFixed(2)}%`;

            var teamRed = document.createElement("span");
            teamRed.style.color = "#ff0000";
            teamRed.innerHTML = `${redAcc.toFixed(2)}%`;

            teamResults.appendChild(teamBlue);
            teamResults.appendChild(document.createTextNode(" vs. "));
            teamResults.appendChild(teamRed);

            var accDifference = Math.abs(blueAcc - redAcc);
            var winner = document.createElement("span");
            winner.classList.add("winner");
            winner.style.fontWeight = "bold";

            if (blueAcc > redAcc)
            {
                winner.style.color = "#0000ff";
                winner.innerHTML = "Blue";
            }
            else if (redAcc > blueAcc)
            {
                winner.style.color = "#ff0000";
                winner.innerHTML = "Red";
            }
            else
            {
                winner.style.color = "#000000";
                winner.innerHTML = "Draw";
            }

            teamResults.appendChild(document.createElement("br"));
            teamResults.appendChild(winner);
            teamResults.appendChild(document.createTextNode(" wins by "));
            teamResults.appendChild(document.createTextNode(accDifference.toFixed(2)));
            teamResults.appendChild(document.createTextNode("%!"));
            return teamResults;

        case 2:
            // Combo
            var blueCombo = 0;
            var redCombo = 0;

            results.forEach(result => {
                if (result.player.team == 1)
                    blueCombo += result.score.max_combo;
                else if (result.player.team == 2)
                    redCombo += result.score.max_combo;
            });

            var teamBlue = document.createElement("span");
            teamBlue.style.color = "#0000ff";
            teamBlue.innerHTML = `${blueCombo.toLocaleString()}`;

            var teamRed = document.createElement("span");
            teamRed.style.color = "#ff0000";
            teamRed.innerHTML = `${redCombo.toLocaleString()}`;

            teamResults.appendChild(teamBlue);
            teamResults.appendChild(document.createTextNode(" vs. "));
            teamResults.appendChild(teamRed);

            var comboDifference = Math.abs(blueCombo - redCombo);
            var winner = document.createElement("span");
            winner.classList.add("winner");
            winner.style.fontWeight = "bold";

            if (blueCombo > redCombo)
            {
                winner.style.color = "#0000ff";
                winner.innerHTML = "Blue";
            }
            else if (redCombo > blueCombo)
            {
                winner.style.color = "#ff0000";
                winner.innerHTML = "Red";
            }
            else
            {
                winner.style.color = "#000000";
                winner.innerHTML = "Draw";
            }

            teamResults.appendChild(document.createElement("br"));
            teamResults.appendChild(winner);
            teamResults.appendChild(document.createTextNode(" wins by "));
            teamResults.appendChild(document.createTextNode(comboDifference.toLocaleString()));
            teamResults.appendChild(document.createTextNode(" combo!"));
            return teamResults;
    }
}

function loadMatchEvents(id, after=undefined)
{
    const statusText = document.getElementById("status-text");
    const container = document.getElementById("match-events");
    let args = "";

    if (after != undefined)
        args = `?after=${after.getTime() - refreshRate}`;

    fetch(`/api/multiplayer/match/${id}/events${args}`)
        .then(response => {
            if (response.error)
                throw response.error;

            return response.json();
        })
        .then(events => {
            statusText.innerHTML = "";

            events.forEach(event => {
                const eventDate = new Date(event.time);
                const eventElement = document.createElement("div");
                eventElement.classList.add("event");

                const timeElement = document.createElement("span");
                timeElement.classList.add("event-time");
                timeElement.innerHTML = `${eventDate.getHours()}:${eventDate.getMinutes()}`;

                switch (event.type)
                {
                    case 0:
                        if (!event.data.name)
                            throw `Invalid api response: ${event.data}`;

                        var userElement = document.createElement("a");
                        userElement.innerHTML = event.data.name;
                        userElement.href = `/u/${event.data.user_id}`;
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(userElement);
                        descriptionElement.appendChild(document.createTextNode(" has joined the match."));
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);
                        break;

                    case 1:
                        if (!event.data.name)
                            throw `Invalid api response: ${event.data}`;

                        var userElement = document.createElement("a");
                        userElement.innerHTML = event.data.name;
                        userElement.href = `/u/${event.data.user_id}`;
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(userElement);
                        descriptionElement.appendChild(document.createTextNode(" has left the match."));
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);
                        break;

                    case 2:
                        if (!event.data.name)
                            throw `Invalid api response: ${event.data}`;

                        var userElement = document.createElement("a");
                        userElement.innerHTML = event.data.name;
                        userElement.href = `/u/${event.data.user_id}`;
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(userElement);
                        descriptionElement.appendChild(document.createTextNode(" was kicked from the match."));
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);
                        break;

                    case 3:
                        if (!event.data.new)
                            throw `Invalid api response: ${event.data}`;

                        var userElement = document.createElement("a");
                        userElement.innerHTML = event.data.new.name;
                        userElement.href = `/u/${event.data.new.id}`;
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(userElement);
                        descriptionElement.appendChild(document.createTextNode(" has become the host."));
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);
                        break;

                    case 4:
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(document.createTextNode("The match was disbanded."));
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);
                        break;

                    case 5:
                        // Match was started
                        // TODO: Display this?
                        break;

                    case 6:
                        var startTime = new Date(event.data.start_time);
                        var endTime = new Date(event.data.end_time);
                        var duration = endTime - startTime;
                        var durationString = `${Math.floor(duration / 1000 / 60)}m ${Math.floor(duration / 1000 % 60)}s`;

                        var teamType = TeamType[event.data.team_mode];
                        var scoringType = ScoringType[event.data.scoring_mode];
                        var mode = Mode[event.data.mode];

                        var matchDetails = document.createElement("div");
                        matchDetails.classList.add("match-details");

                        var durationElement = document.createElement("div");
                        var durationTitle = document.createElement("strong");
                        durationTitle.innerHTML = "Duration: ";
                        durationElement.appendChild(durationTitle);
                        durationElement.appendChild(document.createTextNode(`${durationString}`));

                        var gameModeElement = document.createElement("div");
                        var gameModeTitle = document.createElement("strong");
                        gameModeTitle.innerHTML = "Game Mode: ";
                        gameModeElement.appendChild(gameModeTitle);
                        gameModeElement.appendChild(document.createTextNode(`${mode} (${teamType})`));

                        var scoringTypeElement = document.createElement("div");
                        var scoringTypeTitle = document.createElement("strong");
                        scoringTypeTitle.innerHTML = "Scoring Type: ";
                        scoringTypeElement.appendChild(scoringTypeTitle);
                        scoringTypeElement.appendChild(document.createTextNode(`${scoringType}`));

                        matchDetails.appendChild(durationElement);
                        matchDetails.appendChild(gameModeElement);
                        matchDetails.appendChild(scoringTypeElement);

                        var beatmapDetails = document.createElement("div");
                        var beatmapTitle = document.createElement("strong");
                        beatmapTitle.innerHTML = "Beatmap: ";
                        beatmapDetails.appendChild(beatmapTitle);;

                        if (event.data.beatmap_id != 0)
                        {
                            var beatmapLink = document.createElement("a");
                            beatmapLink.href = `/b/${event.data.beatmap_id}`;
                            beatmapLink.appendChild(beatmapDetails);
                            beatmapLink.innerHTML = event.data.beatmap_text;
                            beatmapDetails.appendChild(beatmapLink);
                        }
                        else
                        {
                            beatmapDetails.appendChild(
                                document.createTextNode(event.data.beatmap_text)
                            );
                        }

                        var beatmapInfo = document.createElement("div");
                        beatmapInfo.classList.add("beatmap-info");
                        beatmapInfo.appendChild(beatmapDetails);

                        eventElement.appendChild(matchDetails);
                        eventElement.appendChild(beatmapInfo);

                        var matchResults = document.createElement("div");
                        matchResults.classList.add("match-results");

                        var resultsTable = generateResultsTable(event.data.results, event.data.mods);

                        matchResults.appendChild(resultsTable);
                        eventElement.appendChild(matchResults);

                        if (event.data.team_mode == 2 || event.data.team_mode == 3)
                        {
                            var teamResults = getTeamWinner(event.data.results, event.data.scoring_mode);
                            eventElement.appendChild(teamResults);
                        }

                        eventElement.classList.add("game");
                        eventElement.classList.remove("event");
                        break;

                    case 7:
                        var descriptionElement = document.createElement("span");
                        descriptionElement.classList.add("event-description");
                        descriptionElement.appendChild(document.createTextNode("The match was aborted!"));
                        descriptionElement.style.color = "#ff0000";
                        eventElement.appendChild(timeElement);
                        eventElement.appendChild(descriptionElement);

                }

                container.appendChild(eventElement);
            });
        })
        .catch(error => {
            document.querySelectorAll(".event").forEach(element => element.remove());
            document.querySelectorAll(".game").forEach(element => element.remove());
            statusText.innerHTML = "Failed to load match. Please try again!";
            console.error(error);
        });
}

function loadMatchEventsLoop() {
    setTimeout(() => {
        var events = document.getElementById("match-events").innerHTML;

        if (events.includes("disbanded"))
            return;

        if (events.includes("closed"))
            return;

        loadMatchEvents(matchId, new Date());
        loadMatchEventsLoop();
    }, refreshRate);
}

// TODO: Add option for displaying chat

document.addEventListener("DOMContentLoaded", () => {
    loadMatchEvents(matchId);
    loadMatchEventsLoop();
});
