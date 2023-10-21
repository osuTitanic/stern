function beatmapSearch()
{
    const inputValue = document.getElementById("beatmap-search").value.trim();

    if (inputValue !== '') {
        window.location.href = `/beatmapsets?q=${encodeURIComponent(inputValue)}`;
        return false;
    }
    return true;
}

function userSearch()
{
    const inputValue = document.getElementById("user-search").value.trim();

    if (inputValue !== '') {
        window.location.href = `/u/${encodeURIComponent(inputValue)}`;
        return false;
    }
    return true;
}

function resetOrPlayAudio(element) {
    var audio = document.getElementById(element)

    if (audio.paused) return audio.play();

    audio.pause();
    audio.currentTime = 0;
}

function showLoginForm()
{
    // TODO
}