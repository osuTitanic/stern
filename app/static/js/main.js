function beatmapSearch()
{
    var inputValue = document.getElementById("beatmap-search").value.trim();

    if (inputValue !== '') {
        window.location.href = '/beatmapsets?query=' + encodeURIComponent(inputValue);
        return false;
    }
    return true;
}

function userSearch()
{
    var inputValue = document.getElementById("user-search").value.trim();

    if (inputValue !== '') {
        window.location.href = '/u/' + encodeURIComponent(inputValue);
        return false;
    }
    return true;
}

function resetOrPlayAudio(element) {
    var audio = document.getElementById(element);

    if (audio.paused) {
        return audio.play();
    }

    audio.pause();
    audio.currentTime = 0;
}

function showLoginForm() {
    $(".login-dropdown").slideToggle(100);
    $("#username-field").select();
}

function toggleSpoiler(root) {
    var spoiler = $(root).parents(".spoiler");
    spoiler.children(".spoiler-body").slideToggle("fast");
    spoiler.find('img').trigger('unveil');
    return false;
}

function loadBBCodePreview(element) {
    var bbcodeWrapper = element.parentElement.parentElement;
    var bbcodeEditor = bbcodeWrapper.querySelector('textarea');
    var form = new FormData();
    form.append('bbcode', bbcodeEditor.value);
    form.append('csrf_token', csrfToken);

    // Remove old previews
    var previews = document.querySelectorAll('.bbcode-preview');
    Array.prototype.forEach.call(previews, function(element) {
        element.parentNode.removeChild(element);
    });

    fetch('/api/bbcode/preview', {
        method: "POST",
        cache: "no-cache",
        body: form
    })
    .then(function(response) {
        if (!response.ok)
            throw new Error(response.status + ': "' + response.statusText + '"');
        return response.text();
    })
    .then(function(htmlPreview) {
        if (!htmlPreview)
            return;

        var previewContainer = document.createElement('div');
        previewContainer.className = 'bbcode-preview bbcode';
        previewContainer.innerHTML = htmlPreview;

        bbcodeWrapper.appendChild(previewContainer);
    })
    .catch(function(error) {
        var previewContainer = document.createElement('div');
        previewContainer.className = 'bbcode-preview bbcode';
        previewContainer.appendChild(
            document.createTextNode('Failed to load bbcode preview :(')
        );
        bbcodeWrapper.appendChild(previewContainer);
        console.error(error);
    });

    return false;
}

function confirmRedirect(url, promptText) {
    if (promptText === undefined) promptText = 'Are you sure?';
    var do_redirect = confirm(promptText);

    if (!do_redirect)
        return;

    window.location.href = url;
    return false;
}

function cookieExists(name) {
    return document.cookie.indexOf(name + '=') !== -1;
}

function isLoggedIn() {
    return cookieExists('session');
}

function show(id) {
    $('#' + id).show();
}

function hide(id) {
    $('#' + id).hide();
}

document.addEventListener("DOMContentLoaded", function() {
    $(".timeago").timeago();
});

const params = new URLSearchParams(location.search);

if (params.get('wait') && location.pathname == '/')
{
    alert('Too many login attempts. Please wait a minute and try again!');
}
