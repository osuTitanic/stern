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

var EventRenderers = {
    [EventTypes.RanksGained]: (data) => {},
    [EventTypes.NumberOne]: (data) => {},
    [EventTypes.BeatmapLeaderboardRank]: (data) => {},
    [EventTypes.LostFirstPlace]: (data) => {},
    [EventTypes.PPRecord]: (data) => {},
    [EventTypes.TopPlay]: (data) => {},
    [EventTypes.AchievementUnlocked]: (data) => {},
    [EventTypes.ScoreSubmitted]: (data) => {},
    [EventTypes.BeatmapUploaded]: (data) => {},
    [EventTypes.BeatmapUpdated]: (data) => {},
    [EventTypes.BeatmapRevived]: (data) => {},
    [EventTypes.BeatmapFavouriteAdded]: (data) => {},
    [EventTypes.BeatmapFavouriteRemoved]: (data) => {},
    [EventTypes.BeatmapRated]: (data) => {},
    [EventTypes.BeatmapCommented]: (data) => {},
    [EventTypes.BeatmapDownloaded]: (data) => {},
    [EventTypes.BeatmapStatusUpdated]: (data) => {},
    [EventTypes.BeatmapNominated]: (data) => {},
    [EventTypes.ForumTopicCreated]: (data) => {},
    [EventTypes.ForumPostCreated]: (data) => {},
    [EventTypes.ForumSubscribed]: (data) => {},
    [EventTypes.ForumUnsubscribed]: (data) => {},
    [EventTypes.ForumBookmarked]: (data) => {},
    [EventTypes.ForumUnbookmarked]: (data) => {},
    [EventTypes.OsuCoinsReceived]: (data) => {},
    [EventTypes.OsuCoinsUsed]: (data) => {},
    [EventTypes.FriendAdded]: (data) => {},
    [EventTypes.FriendRemoved]: (data) => {},
    [EventTypes.ReplayWatched]: (data) => {},
    [EventTypes.ScreenshotUploaded]: (data) => {},
    [EventTypes.UserRegistration]: (data) => {},
    [EventTypes.UserLogin]: (data) => {},
    [EventTypes.UserChatMessage]: (data) => {},
    [EventTypes.UserMatchCreated]: (data) => {},
    [EventTypes.UserMatchJoined]: (data) => {},
    [EventTypes.UserMatchLeft]: (data) => {},
    [EventTypes.BeatmapNuked]: (data) => {}
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

    var renderedEvent = renderer(eventData);
    if (!renderedEvent) {
        console.warn('Renderer returned no content for event type:', eventType);
        return;
    }

    var element = document.createElement('div');
    element.className = 'event-item';
    element.appendChild(renderedEvent);
    return element;
}

function removeEvent(eventElement) {
    eventElement.style.opacity = '0';
    setTimeout(function() { eventElement.remove() }, 1000);
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
