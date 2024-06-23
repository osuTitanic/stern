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
    $(".login-dropdown").slideToggle(100);
    $("#username-field").select();
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
    const bbcodeWrapper = element.parentElement.parentElement;
    const bbcodeEditor = bbcodeWrapper.querySelector('textarea');
    const form = new FormData();
    form.set('bbcode', bbcodeEditor.value);

    // Remove old previews
    document.querySelectorAll('.bbcode-preview').forEach(element => {
        element.remove();
    });

    fetch('/api/bbcode/preview', {
        method: "POST",
        cache: "no-cache",
        body: form
    })
    .then(response => {
        if (!response.ok)
            throw new Error(`${response.status}: "${response.statusText}"`);
        return response.text();
    })
    .then(htmlPreview => {
        if (!htmlPreview)
            return;

        const previewContainer = document.createElement('div');
        previewContainer.classList.add('bbcode-preview', 'bbcode');
        previewContainer.innerHTML = htmlPreview;

        bbcodeWrapper.appendChild(previewContainer);
    })
    .catch(error => {
        const previewContainer = document.createElement('div');
        previewContainer.classList.add('bbcode-preview', 'bbcode');
        previewContainer.appendChild(
            document.createTextNode('Failed to load bbcode preview :(')
        );
        bbcodeWrapper.appendChild(previewContainer);
        console.error(error);
    })

    return false;
}

async function confirmNotification(element)
{
    await fetch(`/api/notifications/confirm?id=${element.id}`);

    if (element.getAttribute("href"))
        window.location.href = element.getAttribute("href");

    element.classList.remove('new');
    element.onclick = () => {};
}

function confirmRedirect(url, prompt)
{
    do_redirect = confirm(prompt);

    if (!do_redirect)
        return;

    window.location.href = url;
    return false;
}

function cookieExists(name) { return document.cookie.indexOf(`${name}=`); }
function isLoggedIn() { return cookieExists('session'); }

function show(id) { $(`#${id}`).show(); }
function hide(id) { $(`#${id}`).hide(); }

const params = new URLSearchParams(location.search);

if (params.get('wait') && location.pathname == '/')
{
    alert('Too many login attempts. Please wait a minute and try again!');
}
