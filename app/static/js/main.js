function beatmapSearch()
{
    const inputValue = document.getElementById("beatmap-search").value.trim();

    if (inputValue !== '') {
        window.location.href = `/beatmapsets?query=${encodeURIComponent(inputValue)}`;
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

function showLoginForm() {
    // TODO: Dropdown animation
    const dropdown = document.querySelector(".login-dropdown");

    if (dropdown.style.display !== "block")
        dropdown.style.display = "block";
    else
        dropdown.style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    $(".timeago").timeago();
});

function toggleSpoiler(root) {
    var spoiler = $(root).parents(".spoiler");
	spoiler.children(".spoiler-body").slideToggle("fast");
	spoiler.find('img').trigger('unveil');
	return false;
}
