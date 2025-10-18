var mainChannelId = 2; // #osu
var socket = null;
var channels = {};
var users = {};

var activeChannel = null;
var activeDM = null;
var messageHistory = {};

var messageHandlers = {
    "part": handleUserPart,
    "quit": handleUserQuit,
    "whois": handleWhoIsResponse,
    "message": handleChannelMessage
}

function initializeSocket(username, password) {
    if (!username || !password) {
        console.error("Username and password are required");
        return;
    }

    socket = io(loungeBackend, {transports: ['polling']});

    socket.onAny((event, ...args) => {
        console.log("Incoming event:", event, args);
    });

    socket.onAnyOutgoing((event, ...args) => {
        console.log("Outgoing event:", event, args);
    });

    socket.on('connect', function() {
        console.log('Connected to IRC backend');
        updateStatusText('Connected to chat server');
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from IRC backend');
        updateStatusText('Disconnected from chat server');
        disableChatInput();
    });

    socket.on('init', function() {
        channels = {};
        users = {};
    });

    socket.on('configuration', function() {
        socket.emit('network:new', {
            nick: username,
            username: username,
            realname: username,
            leaveMessage: "Leaving...",
            join: "#osu",
            password: password
        });
    });

    socket.on('msg', function(data) {
        if (data.msg.type in messageHandlers) {
            messageHandlers[data.msg.type](data);
        }
    });

    socket.on('network', onNetworkConfiguration);
    socket.on('join', onChannelJoin);
    socket.on('topic', onChannelTopic);
    socket.on('users', onChannelUsers);
    socket.on('names', onChannelNames);
}

function resetConnection() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    channels = {};
    users = {};
}

function onNetworkConfiguration(data) {
    // Assuming we only have one network
    var network = data.networks[0];

    // Initialize channels
    for (var i = 0; i < network.channels.length; i++) {
        var channel = network.channels[i];

        // Check if "channel" is actually a channel
        // There's also a "lobby" type, which is used for error messages
        if (channel.type !== "channel") {
            continue;
        }

        channels[channel.id] = channel;
        mainChannelId = channel.id;
    }

    populateChannels();
    populateDMs();

    // Auto-switch to main channel
    if (channels[mainChannelId]) {
        switchToChannel(mainChannelId);
    }
}

function onChannelJoin(data) {
    channels[data.chan.id] = data.chan;
}

function onChannelTopic(data) {
    var channel = channels[data.chan];
    if (!channel) {
        console.error("Received topic for unknown channel:", data.chan);
        return;
    }
    channel.topic = data.topic;
    populateChannels();
}

function onChannelUsers(data) {
    var channel = channels[data.chan];
    if (!channel) {
        console.error("Received user listing request for unknown channel:", data.chan);
        return;
    }
    socket.emit("names", { target: channel.id });
}

function onChannelNames(data) {
    var channel = channels[data.id];
    if (!channel) {
        console.error("Received names for unknown channel:", data.id);
        return;
    }
    channel.users = data.users;

    if (channel.id != mainChannelId) {
        // We are not in the main channel
        return;
    }

    if (channel.users.length == users.length) {
        // No change in user count
        return;
    }

    // Request whois info about each user to resolve their user ID
    for (var i = 0; i < data.users.length; i++) {
        // Check if user already exists
        if (getUserByName(data.users[i].nick)) {
            continue;
        }
        sendWhoIs(data.users[i].nick);
    }
}

function handleUserPart(data) {
    var channel = channels[data.chan];
    if (!channel) {
        console.error("Received user part for unknown channel:", data.chan);
        return;
    }

    // Remove user from channel's user list
    for (var nick in channel.users) {
        if (channel.users[nick].nick === data.msg.from.nick) {
            delete channel.users[nick];
        }
    }
}

function handleUserQuit(data) {
    for (var id in users) {
        if (users[id].nick === data.msg.from.nick) {
            delete users[id];
        }
    }
}

function handleWhoIsResponse(data) {
    var whois = data.msg.whois;
    if (!whois || !whois.nick) {
        console.error("Invalid whois data:", data);
        return;
    }

    // Parse user ID from ident
    // "http://osu.titanic.sh/u/12345"
    var identParts = whois.ident.split("/");
    var userId = parseInt(identParts[identParts.length - 1]);
    users[userId] = whois;
    users[userId].id = userId;
    users[userId].status = null;
}

function handleChannelMessage(data) {
    var channel = channels[data.chan];
    if (!channel) {
        console.error("Received message for unknown channel:", data.chan);
        return;
    }

    var sender = getUserByName(data.msg.from.nick);
    if (!sender) {
        sender = { nick: data.msg.from.nick };
    }

    var message = data.msg.text;
    var highlight = data.msg.highlight;

    // Store message in history
    if (!messageHistory[data.chan]) {
        messageHistory[data.chan] = [];
    }
    messageHistory[data.chan].push({
        sender: sender,
        text: message,
        highlight: highlight,
        time: data.msg.time || new Date()
    });

    if (channel.type === "channel") {
        // Display the message if we're in this channel
        if (activeChannel && activeChannel.id === data.chan) {
            displayMessage(sender, message, highlight, data.msg.time);
        }
        console.log(channel.name, sender.nick + ":", message);
    }

    if (channel.type === "query") {
        // Display the message if we're in this DM
        if (activeDM && sender.id === activeDM) {
            displayMessage(sender, message, false, data.msg.time);
        }
        console.log("[DM] ", sender.nick + ":", message);
    }
}

function sendWhoIs(username) {
    sendInput(2, "/whois " + username);
}

function sendWhoIsMany(usernames) {
    if (!usernames || usernames.length === 0) {
        console.error("Usernames array is empty");
        return;
    }
    sendInput(2, "/whois " + usernames.join(" "));
}

function sendChannelMessage(channel, message) {
    if (!channel || !message) {
        console.error("Channel and message are required to send a channel message");
        return;
    }
    sendInput(channel, message);
}

function sendDirectMessage(username, message) {
    if (!username || !message) {
        console.error("Username and message are required to send a direct message");
        return;
    }
    var channel = getChannelByName(username);
    sendInput(channel.id, message);
}

function sendInput(channel, message) {
    if (!socket) {
        console.error("Socket is not initialized");
        return;
    }
    if (!channel || !message) {
        console.error("Channel and message are required to send input");
        return;
    }
    socket.emit("input", { target: channel, text: message });
}

function getChannelByName(name) {
    for (var id in channels) {
        if (channels[id].name === name) {
            return channels[id];
        }
    }
    return null;
}

function getChannelById(channelId) {
    return channels[channelId] || null;
}

function getUserByName(username) {
    for (var id in users) {
        if (users[id].nick === username) {
            return users[id];
        }
    }
    return null;
}

function getUserById(userId) {
    return users[userId] || null;
}

function fetchChannelMessageHistory(channel, offset, limit, onSuccess, onFailure) {
    var url = "/chat/channels/" + encodeURIComponent(channel) + "/messages";

    if (offset) {
        url += "?offset=" + encodeURIComponent(offset);
    }
    if (limit) {
        url += (offset ? "&" : "?") + "limit=" + encodeURIComponent(limit);
    }

    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }

        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch channel message history:", xhr);
        onFailure(xhr);
    });
}

function fetchDirectMessageHistory(userId, offset, limit, onSuccess, onFailure) {
    var url = "/chat/dms/" + userId + "/messages";

    if (offset) {
        url += "?offset=" + encodeURIComponent(offset);
    }
    if (limit) {
        url += (offset ? "&" : "?") + "limit=" + encodeURIComponent(limit);
    }

    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }

        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch DM message history:", xhr);
        onFailure(xhr);
    });
}

function fetchUserById(userId, onSuccess, onFailure) {
    var url = "/users/" + userId;
    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }
        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch user by ID:", xhr);
        onFailure(xhr);
    });
}

function fetchUserByName(username, onSuccess, onFailure) {
    var url = "/users/lookup/" + encodeURIComponent(username);
    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }
        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch user by name:", xhr);
        onFailure(xhr);
    });
}

function fetchUserStatus(userId, onSuccess, onFailure) {
    var url = "/users/" + userId + "/status";
    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }
        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch user status:", xhr);
        onFailure(xhr);
    });
}

function fetchDirectMessageSelection(onSuccess, onFailure) {
    var url = "/chat/dms";

    return performApiRequest("GET", url, null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (!response) {
            console.error("Invalid response format:", response);
            onFailure(xhr);
            return;
        }
        onSuccess(response);
    }, function(xhr) {
        console.error("Failed to fetch DM selection:", xhr);
        onFailure(xhr);
    });
}

function populateChannels() {
    var channelContainer = document.getElementById("channel-container");

    // Nuke everything first
    while (channelContainer.firstChild) {
        channelContainer.removeChild(channelContainer.firstChild);
    }

    for (var id in channels) {
        var channel = channels[id];
        if (channel.type !== "channel") {
            continue;
        }

        var channelElement = document.createElement("div");
        channelElement.className = "channel-entry";
        channelElement.textContent = channel.name;
        channelElement.title = channel.topic || "No topic set";
        channelElement.id = "channel-" + channel.id;
        channelElement.dataset.channelId = channel.id;
        channelElement.addEventListener("click", function() {
            switchToChannel(parseInt(this.dataset.channelId));
        });

        // Mark active channel
        if (activeChannel && activeChannel.id === channel.id) {
            channelElement.classList.add("active");
        }

        channelContainer.appendChild(channelElement);
    }
}

function populateDMs() {
    var dmContainer = document.getElementById("dm-container");

    
    fetchDirectMessageSelection(function(dms) {
        if (!dms || dms.length === 0) {
            var errorElement = document.getElementById("dm-status");
            if (errorElement) {
                errorElement.textContent = "No DMs available.";
                errorElement.style.display = "block";
            }
            return;
        }

        // Nuke everything first
        while (dmContainer.firstChild) {
            dmContainer.removeChild(dmContainer.firstChild);
        }

        for (var i = 0; i < dms.length; i++) {
            var dm = dms[i];
            var dmElement = document.createElement("div");
            dmElement.className = "dm-entry";
            dmElement.textContent = dm.user.name;
            dmElement.dataset.userId = dm.user.id;
            dmElement.addEventListener("click", function() {
                switchToDM(parseInt(this.dataset.userId));
            });

            // Mark active DM
            if (activeDM && activeDM === dm.user.id) {
                dmElement.classList.add("active");
            }

            dmContainer.appendChild(dmElement);
        }
    }, function(xhr) {
        var errorElement = document.getElementById("dm-status");
        if (errorElement) {
            errorElement.textContent = "Failed to load DMs.";
            errorElement.style.display = "block";
        }
    });
}

function switchToChannel(channelId) {
    var channel = channels[channelId];
    if (!channel) {
        console.error("Channel not found:", channelId);
        return;
    }

    activeChannel = channel;
    activeDM = null;

    // Update UI to show active channel
    populateChannels();
    updateChatTitle(channel.name);

    // Clear and reload chat log
    clearChatLog();
    loadChannelHistory(channel);
    enableChatInput();
}

function switchToDM(userId) {
    activeDM = userId;
    activeChannel = null;

    // Update UI to show active DM
    populateChannels();
    populateDMs();

    fetchUserById(userId, function(user) {
        updateChatTitle("Direct Message with " + user.name);

        // Clear and reload chat log
        clearChatLog();
        loadDMHistory(user);
        enableChatInput();
    }, function(xhr) {
        console.error("Failed to fetch user for DM:", xhr);
        updateStatusText("Failed to load DM");
    });
}

function loadChannelHistory(channel) {
    updateStatusText("Loading messages...");
    
    fetchChannelMessageHistory(channel.name, 0, 50, function(messages) {
        if (!messages || messages.length === 0) {
            updateStatusText("No messages in this channel yet.");
            return;
        }

        // Display messages in order (reversed)
        for (var i = messages.length - 1; i >= 0; i--) {
            var msg = messages[i];
            displayHistoricalMessage(msg);
        }

        updateStatusText("Type a message...");
        scrollChatToBottom();
    }, function(xhr) {
        console.error("Failed to load channel history:", xhr);
        updateStatusText("Failed to load message history.");
    });
}

function loadDMHistory(user) {
    updateStatusText("Loading messages...");
    
    fetchDirectMessageHistory(user.id, 0, 50, function(messages) {
        if (!messages || messages.length === 0) {
            updateStatusText("No messages yet. Start a conversation!");
            return;
        }

        // Display messages in order (reversed)
        for (var i = messages.length - 1; i >= 0; i--) {
            var msg = messages[i];
            displayHistoricalDirectMessage(msg, user);
        }

        updateStatusText("Type a message...");
        scrollChatToBottom();
    }, function(xhr) {
        console.error("Failed to load DM history:", xhr);
        updateStatusText("Failed to load message history.");
    });
}

function displayMessage(sender, text, highlight, time) {
    var chatLog = document.querySelector(".chat-log");
    if (!chatLog) {
        console.error("Chat log element not found");
        return;
    }

    var messageElement = document.createElement("div");
    messageElement.className = "chat-message-entry";

    if (highlight) {
        messageElement.classList.add("highlighted");
    }

    var timestamp = time ? formatMessageTime(time) : formatMessageTime(new Date());
    var senderName = sender.nick || sender.name || "Unknown";
    var userId = sender.id;

    var timestampSpan = document.createElement("span");
    timestampSpan.className = "message-time";
    timestampSpan.textContent = timestamp;

    var senderSpan = document.createElement("span");
    senderSpan.className = "message-sender";
    senderSpan.textContent = senderName;

    if (userId) {
        senderSpan.style.cursor = "pointer";
        senderSpan.dataset.userId = userId;
        senderSpan.addEventListener("click", function() {
            window.location.href = "/users/" + this.dataset.userId;
        });
    }

    var textSpan = document.createElement("span");
    textSpan.className = "message-text";
    textSpan.textContent = text;

    messageElement.appendChild(timestampSpan);
    messageElement.appendChild(document.createTextNode(" "));
    messageElement.appendChild(senderSpan);
    messageElement.appendChild(document.createTextNode(": "));
    messageElement.appendChild(textSpan);

    chatLog.appendChild(messageElement);
    scrollChatToBottom();
}

function displayHistoricalMessage(msg) {
    displayMessage(
        { nick: msg.sender.name, id: msg.sender_id },
        msg.message,
        false,
        new Date(msg.time)
    );
}

function displayHistoricalDirectMessage(msg, user) {
    var nickname = currentUsername;
    if (msg.sender_id === user.id) {
        nickname = user.name;
    }

    displayMessage(
        { nick: nickname, id: msg.sender_id },
        msg.message,
        false,
        new Date(msg.time)
    );
}

function formatMessageTime(time) {
    var date = time instanceof Date ? time : new Date(time);
    var hours = date.getHours().toString().padStart(2, '0');
    var minutes = date.getMinutes().toString().padStart(2, '0');
    return hours + ":" + minutes;
}

function clearChatLog() {
    var chatLog = document.querySelector(".chat-log");
    if (!chatLog) {
        return;
    }

    while (chatLog.firstChild) {
        chatLog.removeChild(chatLog.firstChild);
    }
}

function scrollChatToBottom() {
    var chatLog = document.querySelector(".chat-log");
    if (chatLog) {
        chatLog.scrollTop = chatLog.scrollHeight;
    }
}

function updateChatTitle(title) {
    var statusText = document.querySelector(".chat-input .status-text");
    if (statusText) {
        statusText.textContent = title;
    }
}

function updateStatusText(text) {
    var statusText = document.querySelector(".chat-input .chat-message");
    if (statusText) {
        statusText.placeholder = text;
    }
}

function enableChatInput() {
    var inputField = document.querySelector(".chat-input .chat-message");
    var sendButton = document.querySelector(".chat-input .chat-send");

    if (inputField) {
        inputField.disabled = false;
        inputField.placeholder = "Type a message...";
    }

    if (sendButton) {
        sendButton.disabled = false;
    }
}

function disableChatInput() {
    var inputField = document.querySelector(".chat-input .chat-message");
    var sendButton = document.querySelector(".chat-input .chat-send");
    
    if (inputField) {
        inputField.disabled = true;
        inputField.placeholder = "Connecting...";
    }
    
    if (sendButton) {
        sendButton.disabled = true;
    }
}

function sendCurrentMessage() {
    var inputField = document.querySelector(".chat-input .chat-message");
    if (!inputField) {
        return;
    }

    var message = inputField.value.trim();
    if (!message) {
        return;
    }

    if (activeChannel) {
        sendChannelMessage(activeChannel.id, message);
        inputField.value = "";
    } else if (activeDM) {
        fetchUserById(activeDM, function(user) {
            sendDirectMessage(user.name, message);
            inputField.value = "";
            
            // Optionally display the sent message immediately
            displayMessage(
                { nick: currentUsername, id: currentUser },
                message,
                false,
                new Date()
            );
        }, function(xhr) {
            console.error("Failed to send DM:", xhr);
            updateStatusText("Failed to send message");
        });
    } else {
        console.error("No active channel or DM selected");
    }
}

function initializeChatHandlers() {
    var sendButton = document.querySelector(".chat-input .chat-send");
    var inputField = document.querySelector(".chat-input .chat-message");

    if (sendButton) {
        sendButton.addEventListener("click", sendCurrentMessage);
    }

    if (inputField) {
        inputField.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                sendCurrentMessage();
            }
        });
    }
}

function onIrcTokenResponse(xhr) {
    var response = JSON.parse(xhr.responseText);
    if (!response || !response.token)
    {
        console.error("Invalid response format or missing token:", response);
        alert("Failed to retrieve your IRC password. Please try again later!");
        return;
    }
    initializeSocket(currentUsername, response.token);
}

function onIrcTokenFailure(xhr) {
    console.error("Failed to retrieve IRC token:", xhr);
    alert("Failed to retrieve your IRC password. Please try again later!");
}

addEvent("DOMContentLoaded", document, function() {
    if (!isLoggedIn())
        return;

    initializeChatHandlers();
    fetchIrcToken(onIrcTokenResponse, onIrcTokenFailure);
});
