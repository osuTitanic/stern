
function WebSocketApiResolver() {
    return window.WebSocket || window.MozWebSocket;
}

function supportsWebSockets() {
    try {
        return Boolean(WebSocketApiResolver());
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

    var WebSocket = WebSocketApiResolver();
    var WebSocketUrl = activityContainer.dataset.wsEndpoint;
    console.info('Connecting to WebSocket at:', WebSocketUrl);

    var socket = new WebSocket(WebSocketUrl);
    socket.onopen = onWebSocketOpen;
    socket.onmessage = onWebSocketMessage;
    socket.onerror = onWebSocketError;
    socket.onclose = onWebSocketClose;
}

function onWebSocketOpen(event) {
    console.info('Websocket connection established:', event);

    var statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.textContent = 'Connected!';
        statusText.style.opacity = '0';
    }
}

function onWebSocketMessage(event) {
    var statusText = document.getElementById('status-text');

    try {
        const data = JSON.parse(event.data);
        console.info('Websocket message received:', data);
    } catch (e) {
        console.error('Failed to parse websocket message:', event.data, e);
        if (statusText) {
            statusText.textContent = 'Error processing message.';
            statusText.style.opacity = '1';
        }
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

addEvent('DOMContentLoaded', document, function() {
    var activityContainer = document.getElementById('activity-feed-container');

    if (!activityContainer) {
        console.error('Activity feed container not found!');
        return;
    }

    var statusText = document.createElement('p');
    statusText.textContent = 'Connecting to websocket...';
    statusText.style.opacity = '1';
    statusText.id = 'status-text';
    activityContainer.appendChild(statusText);

    if (!supportsWebSockets()) {
        statusText.textContent = 'WebSockets are not supported by your browser.';
        console.warn('WebSockets are not supported by this browser.');
        return;
    }

    setupWebSocket();
});
