var socket = null;
var channels = {};

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
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from IRC backend');
    });
    
    socket.on('init', function() {
        channels = {};
    });

    socket.on('configuration', function() {
        socket.emit("network:new", {
            nick: username,
            username: username,
            realname: username,
            leaveMessage: "Leaving...",
            join: "#osu",
            password: password
        });
    });

    socket.on("network", onNetworkConfiguration);
    socket.on("join", onChannelJoin);
    socket.on("topic", onChannelTopic);
    socket.on("users", onChannelUsers);
    socket.on("names", onChannelNames);
}

function resetConnection() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    channels = {};
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

    fetchIrcToken(onIrcTokenResponse, onIrcTokenFailure);
});
