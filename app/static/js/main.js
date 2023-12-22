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

function loadBBCodePreview(element) {
    const bbcodeWrapper = element.parentElement;
    const bbcodeEditor = bbcodeWrapper.querySelector('textarea');
    const form = new FormData();
    form.set('bbcode', bbcodeEditor.value);

    fetch('/api/bbcode/preview', {
        method: "POST",
        cache: "no-cache",
        body: form
    })
    .then(response => {
        if (!response.ok)
            throw new Error(response.status);
        return response.text();
    })
    .then(htmlPreview => {
        // Remove old previews
        document.querySelectorAll('.bbcode-preview').forEach(element => {
            element.remove();
        });

        const previewContainer = document.createElement('div');
        previewContainer.classList.add('bbcode-preview', 'bbcode')
        previewContainer.innerHTML = htmlPreview

        bbcodeWrapper.appendChild(previewContainer);
    })
    .catch(error => {
        console.error(error);
    })

    return false;
}
