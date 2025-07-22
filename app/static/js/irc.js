function fetchIrcToken(onSuccess, onFailure)
{
    if (!isLoggedIn())
    {
        console.error("User is not logged in, cannot fetch IRC token.");
        return;
    }

    return performApiRequest("GET", "/account/irc/token", null, onSuccess, onFailure);
}

function regenerateIrcToken(onSuccess, onFailure)
{
    if (!isLoggedIn())
    {
        console.error("User is not logged in, cannot fetch IRC token.");
        return;
    }

    return performApiRequest("POST", "/account/irc/token", null, onSuccess, onFailure);
}