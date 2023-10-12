
function beatmapSearch() {
    const inputValue = document.getElementById("beatmap-search").value.trim();

    if (inputValue !== '') {
        window.location.href = `/beatmapsets?q=${encodeURIComponent(inputValue)}`;
        return false;
    }
    return true;
}

function userSearch() {
    const inputValue = document.getElementById("user-search").value.trim();

    if (inputValue !== '') {
        window.location.href = `/u/${encodeURIComponent(inputValue)}`;
        return false;
    }
    return true;
}
