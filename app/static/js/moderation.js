var defaultError = {
    "error": 500,
    "details": "An internal server error occurred."
}

function handleApiErrorCallback(xhr, handlerFunction) {
    var error = defaultError;
    try { error = JSON.parse(xhr.responseText); } catch (e) {}
    if (handlerFunction) { handlerFunction(error); }
}

function getUser(userId, onSuccess, onFailure) {
    var url = "/moderation/users/" + userId + "/profile";

    performApiRequest("GET", url, null, function(xhr) {
        var user = JSON.parse(xhr.responseText);
        if (onSuccess) { onSuccess(user); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function updateUserProfile(userId, data, onSuccess, onFailure) {
    getUser(userId, function(user) {
        var profileUpdate = {
            country: user.country,
            email: user.email,
            is_bot: user.is_bot,
            activated: user.activated,
            discord_id: user.discord_id,
            userpage: user.userpage,
            signature: user.signature,
            title: user.title,
            banner: user.banner,
            website: user.website,
            discord: user.discord,
            twitter: user.twitter,
            location: user.location,
            interests: user.interests
        }

        // Update fields provided in "data"
        for (var key in data) {
            if (data.hasOwnProperty(key) && profileUpdate.hasOwnProperty(key)) {
                profileUpdate[key] = data[key];
            }
        }

        var url = "/moderation/users/" + userId + "/profile";

        performApiRequest("PATCH", url, profileUpdate, function(xhr) {
            var user = JSON.parse(xhr.responseText);
            if (onSuccess) { onSuccess(user); }
        }, function(xhr) {
            var error = defaultError;
            try { error = JSON.parse(xhr.responseText); } catch (e) {}
            if (onFailure) { onFailure(error); }
        });
    }, function(error) {
        return onFailure(error);
    });
}

function removeUserAvatar(userId, onSuccess, onFailure) {
    performApiRequest("DELETE", "/moderation/users/" + userId + "/avatar", null, function(xhr) {
        if (onSuccess) { onSuccess(); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function addBadge(userId, badgeData, onSuccess, onFailure) {
    performApiRequest("POST", "/moderation/users/" + userId + "/badges", badgeData, function(xhr) {
        var badge = JSON.parse(xhr.responseText);
        if (onSuccess) { onSuccess(badge); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function removeBadge(userId, badgeId, onSuccess, onFailure) {
    performApiRequest("DELETE", "/moderation/users/" + userId + "/badges/" + badgeId, null, function(xhr) {
        if (onSuccess) { onSuccess(); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function getUserInfringements(userId, onSuccess, onFailure) {
    performApiRequest("GET", "/moderation/users/" + userId + "/infringements", null, function(xhr) {
        var infringements = JSON.parse(xhr.responseText);
        if (onSuccess) { onSuccess(infringements); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function createUserInfringement(userId, infringementData, onSuccess, onFailure) {
    performApiRequest("POST", "/moderation/users/" + userId + "/infringements", infringementData, function(xhr) {
        var infringement = JSON.parse(xhr.responseText);
        if (onSuccess) { onSuccess(infringement); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function updateUserInfringement(userId, infringementId, infringementData, onSuccess, onFailure) {
    performApiRequest("PATCH", "/moderation/users/" + userId + "/infringements/" + infringementId, infringementData, function(xhr) {
        var infringement = JSON.parse(xhr.responseText);
        if (onSuccess) { onSuccess(infringement); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function deleteUserInfringement(userId, infringementId, onSuccess, onFailure) {
    performApiRequest("DELETE", "/moderation/users/" + userId + "/infringements/" + infringementId, null, function(xhr) {
        if (onSuccess) { onSuccess(); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function wipeUserScores(userId, onSuccess, onFailure) {
    performApiRequest("DELETE", "/moderation/users/" + userId + "/scores", null, function(xhr) {
        if (onSuccess) { onSuccess(); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function restoreUserScores(userId, onSuccess, onFailure) {
    performApiRequest("POST", "/moderation/users/" + userId + "/scores/restore", null, function(xhr) {
        if (onSuccess) { onSuccess(); }
    }, function(xhr) {
        return handleApiErrorCallback(xhr, onFailure);
    });
}

function deleteUserAccount(userId, onSuccess, onFailure) {
    // TODO
}

function clearUserProfile(userId, onSuccess, onFailure) {
    var data = {
        userpage: null,
        signature: null,
        title: null,
        banner: null,
        website: null,
        discord: null,
        twitter: null,
        location: null,
        interests: null
    };
    updateUserProfile(userId, data, onSuccess, onFailure);
}

function updateUserCountry(userId, countryCode, onSuccess, onFailure) {
    var data = { country: countryCode.toUpperCase() };
    updateUserProfile(userId, data, onSuccess, onFailure);
}

function unlinkDiscord(userId, onSuccess, onFailure) {
    var data = { discord_id: null };
    updateUserProfile(userId, data, onSuccess, onFailure);
}

function setDiscord(userId, discordId, onSuccess, onFailure) {
    var data = { discord_id: discordId };
    updateUserProfile(userId, data, onSuccess, onFailure);
}

function setBotStatus(userId, isBot, onSuccess, onFailure) {
    var data = { is_bot: isBot };
    updateUserProfile(userId, data, onSuccess, onFailure);
}

function changeEmail(userId, newEmail, onSuccess, onFailure) {
    var data = { email: newEmail };
    updateUserProfile(userId, data, onSuccess, onFailure);
}
