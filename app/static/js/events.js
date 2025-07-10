var EventTypes = {
    RanksGained: 1,
    NumberOne: 2,
    BeatmapLeaderboardRank: 3,
    LostFirstPlace: 4,
    PPRecord: 5,
    TopPlay: 6,
    AchievementUnlocked: 7,
    ScoreSubmitted: 8,
    BeatmapUploaded: 9,
    BeatmapUpdated: 10,
    BeatmapRevived: 11,
    BeatmapFavouriteAdded: 12,
    BeatmapFavouriteRemoved: 13,
    BeatmapRated: 14,
    BeatmapCommented: 15,
    BeatmapDownloaded: 16,
    BeatmapStatusUpdated: 17,
    BeatmapNominated: 18,
    ForumTopicCreated: 19,
    ForumPostCreated: 20,
    ForumSubscribed: 21,
    ForumUnsubscribed: 22,
    ForumBookmarked: 23,
    ForumUnbookmarked: 24,
    OsuCoinsReceived: 25,
    OsuCoinsUsed: 26,
    FriendAdded: 27,
    FriendRemoved: 28,
    ReplayWatched: 29,
    ScreenshotUploaded: 30,
    UserRegistration: 31,
    UserLogin: 32,
    UserChatMessage: 33,
    UserMatchCreated: 34,
    UserMatchJoined: 35,
    UserMatchLeft: 36,
    BeatmapNuked: 37
};

var LoginClient = {
    osu: 'osu!',
    irc: 'IRC'
}

var EventRenderers = {
    [EventTypes.RanksGained]: (event) => {},
    [EventTypes.NumberOne]: (event) => {},
    [EventTypes.BeatmapLeaderboardRank]: (event) => {},
    [EventTypes.LostFirstPlace]: (event) => {},
    [EventTypes.PPRecord]: (event) => {},
    [EventTypes.TopPlay]: (event) => {},
    [EventTypes.AchievementUnlocked]: (event) => {},
    [EventTypes.ScoreSubmitted]: (event) => {},
    [EventTypes.BeatmapUploaded]: (event) => {},
    [EventTypes.BeatmapUpdated]: (event) => {},
    [EventTypes.BeatmapRevived]: (event) => {},
    [EventTypes.BeatmapFavouriteAdded]: (event) => {},
    [EventTypes.BeatmapFavouriteRemoved]: (event) => {},
    [EventTypes.BeatmapRated]: (event) => {},
    [EventTypes.BeatmapCommented]: (event) => {},
    [EventTypes.BeatmapDownloaded]: (event) => {},
    [EventTypes.BeatmapStatusUpdated]: (event) => {},
    [EventTypes.BeatmapNominated]: (event) => {},
    [EventTypes.BeatmapNuked]: (event) => {},
    [EventTypes.ForumTopicCreated]: (event) => {},
    [EventTypes.ForumPostCreated]: (event) => {},
    [EventTypes.ForumSubscribed]: (event) => {},
    [EventTypes.ForumUnsubscribed]: (event) => {},
    [EventTypes.ForumBookmarked]: (event) => {},
    [EventTypes.ForumUnbookmarked]: (event) => {},
    [EventTypes.OsuCoinsReceived]: (event) => {},
    [EventTypes.OsuCoinsUsed]: (event) => {},
    [EventTypes.FriendAdded]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " is now following ",
            renderProfile(event.data.target_username, event.data.target_id)
        ];
    },
    [EventTypes.FriendRemoved]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " is no longer following ",
            renderProfile(event.data.target_username, event.data.target_id)
        ];
    },
    [EventTypes.ReplayWatched]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " downloaded a replay on ",
            renderBeatmap(event.data.beatmap_name, event.data.beatmap_id),
            " (", renderScoreLink("download", event.data.score_id), ")"
        ];
    },
    [EventTypes.ScreenshotUploaded]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id), " uploaded a screenshot"
        ];
    },
    [EventTypes.UserRegistration]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id), " just registered!"
        ];
    },
    [EventTypes.UserLogin]: (event) => {
        var profileLink = renderProfile(event.data.username, event.user_id);
        var text = " logged in to the website";

        if (event.data.location == "bancho") {
            var clientType = LoginClient[event.data.client] || event.data.client;
            text = ` logged in to Bancho using ${clientType}`;

            if (event.data.version !== undefined) {
                text += ` (${event.data.version})`;
            }
        }

        return [profileLink, text];
    },
    [EventTypes.UserMatchCreated]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " created a new match: ",
            renderMatchLink(event.data.match_name, event.data.match_id)
        ];
    },
    [EventTypes.UserMatchJoined]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " joined the match: ",
            renderMatchLink(event.data.match_name, event.data.match_id)
        ]
    },
    [EventTypes.UserMatchLeft]: (event) => {
        return [
            renderProfile(event.data.username, event.user_id),
            " left the match: ",
            renderMatchLink(event.data.match_name, event.data.match_id)
        ];
    }
};

function webSocketApiResolver() {
    return window.WebSocket || window.MozWebSocket;
}

function supportsWebSockets() {
    try {
        return Boolean(webSocketApiResolver());
    } catch (e) {
        return false;
    }
}

function setupWebSocket() {
    var activityContainer = document.getElementById('activity-feed-container');
    var statusText = document.getElementById('status-text');

    if (!activityContainer || !statusText) {
        console.error('Activity feed container or status text not found!');
        return;
    }

    var webSocket = webSocketApiResolver();
    var webSocketUrl = activityContainer.dataset.wsEndpoint;
    console.info('Connecting to websocket at:', webSocketUrl);
    statusText.textContent = 'Connecting to websocket...';

    var socket = new webSocket(webSocketUrl);
    socket.onopen = onWebSocketOpen;
    socket.onmessage = onWebSocketMessage;
    socket.onerror = onWebSocketError;
    socket.onclose = onWebSocketClose;
}

function onWebSocketOpen(event) {
    console.info('Websocket connection established:', event);

    var statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.textContent = 'Connected! Waiting for data...';
    }
}

function onWebSocketMessage(event) {
    var activityContainer = document.getElementById('activity-feed-container');
    var statusText = document.getElementById('status-text');

    if (statusText.style.opacity !== '0') {
        statusText.textContent = 'Connected!';
        statusText.style.opacity = '0';
    }

    try {
        var data = JSON.parse(event.data);
        console.info('Websocket message received:', data);

        var eventElement = renderEvent(data);
        if (!eventElement) return;

        activityContainer.insertBefore(eventElement, activityContainer.firstChild);
        setTimeout(function() { removeEvent(eventElement) }, 10000);
    } catch (e) {
        if (statusText) {
            statusText.textContent = 'Error processing message.';
            statusText.style.opacity = '1';
        }
        console.error('Failed to parse websocket message:', event.data, e);
        return;
    }
}

function onWebSocketError(event) {
    console.error('Websocket error:', event);

    var statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.textContent = 'Something went wrong :(';
        statusText.style.opacity = '1';
    }
}

function onWebSocketClose(event) {
    console.warn('Websocket connection closed:', event);

    var statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.textContent = 'Connection closed. Reconnecting...';
        statusText.style.opacity = '1';
    }

    setTimeout(setupWebSocket, 5000);
}

function renderEvent(eventData) {
    var eventType = eventData.type;
    var renderer = EventRenderers[eventType];

    if (!renderer) {
        console.warn('No renderer found for event type:', eventType);
        return;
    }

    var processedEventData = renderer(eventData);
    if (!processedEventData) {
        console.warn('Renderer returned no content for event type:', eventType);
        return;
    }

    // If renderer returns a single element, wrap it in an array
    if (!Array.isArray(processedEventData)) {
        processedEventData = [processedEventData];
    }

    var element = document.createElement('div');
    element.className = 'event-item';
    element.style.opacity = '1';

    // Append event data elements
    processedEventData.forEach(function(e) {
        if (typeof e === 'string') {
            var textNode = document.createTextNode(e);
            element.appendChild(textNode);
        } else {
            element.appendChild(e);
        }
    });

    return element;
}

function renderProfile(username, userId) {
    var profileLink = document.createElement('a');
    profileLink.textContent = username;
    profileLink.href = `/u/${userId}`;
    profileLink.className = 'username-link';
    return profileLink;
}

function renderBeatmap(beatmapName, beatmapId) {
    var beatmapLink = document.createElement('a');
    beatmapLink.textContent = beatmapName;
    beatmapLink.href = `/b/${beatmapId}`;
    beatmapLink.className = 'beatmap-link';
    return beatmapLink;
}

function renderScoreLink(linkText, scoreId) {
    var replayLink = document.createElement('a');
    replayLink.textContent = linkText;
    replayLink.href = `/scores/${scoreId}/download`;
    replayLink.className = 'replay-link';
    return replayLink;
}

function renderMatchLink(matchName, matchId) {
    var matchLink = document.createElement('a');
    matchLink.textContent = matchName;
    matchLink.href = `/mp/${matchId}`;
    matchLink.className = 'match-link';
    return matchLink;
}

function removeEvent(eventElement) {
    if (totalEvents() <= 5) {
        // Wait until enough events are present before removing
        setTimeout(function() { removeEvent(eventElement) }, 1000);
        return;
    }
    eventElement.style.opacity = '0';
    setTimeout(function() { eventElement.remove() }, 1000);
}

function totalEvents() {
    var activityContainer = document.getElementById('activity-feed-container');
    if (!activityContainer) return 0;
    return activityContainer.children.length;
}

addEvent('DOMContentLoaded', document, function() {
    var activityContainer = document.getElementById('activity-feed-container');
    var statusText = document.getElementById('status-text');

    if (!activityContainer) {
        statusText.textContent = 'Activity feed container not found.';
        console.error('Activity feed container not found!');
        return;
    }

    if (!supportsWebSockets()) {
        statusText.textContent = 'WebSockets are not supported by your browser.';
        console.warn('WebSockets are not supported by this browser.');
        return;
    }

    setupWebSocket();
});
