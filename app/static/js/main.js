function addEvent(eventName, targetElement, func) {
    if (targetElement.addEventListener) {
        // DOM Level 2 (modern browsers)
        return targetElement.addEventListener(eventName, func, false);
    }
    if (targetElement.attachEvent) {
        // Older IE (IE8 and earlier)
        return targetElement.attachEvent("on" + eventName, function() {
            return func.call(targetElement, window.event);
        });
    }
    // Fallback to DOM Level 0 (very old browsers)
    targetElement["on"+eventName] = func;
}

function getParentElement(element) {
    // IE8 and earlier doesn't support parentElement, so we use parentNode instead.
    return element.parentElement || (element.parentNode && element.parentNode.nodeType === 1 ? element.parentNode : null);
}

function beatmapSearch() {
    var inputValue = document.getElementById("beatmap-search").value.trim();

    if (inputValue !== '') {
        window.location.href = '/beatmapsets?query=' + encodeURIComponent(inputValue);
        return false;
    }
    return true;
}

function userSearch() {
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

function slideDown(elem) {
    elem.style.height = elem.scrollHeight + "px";
}

function slideUp(elem) {
    elem.style.height = "0px";
}

function loadBBCodePreview(element) {
    var parentElement = getParentElement(element);
    var bbcodeWrapper = getParentElement(parentElement);
    var bbcodeEditor = bbcodeWrapper.querySelector('textarea');
    var form = new FormData();
    form.append('bbcode', bbcodeEditor.value);
    form.append('csrf_token', csrfToken);

    // Remove old previews
    var previews = document.querySelectorAll('.bbcode-preview');
    Array.prototype.forEach.call(previews, function (element) {
        element.parentNode.removeChild(element);
    });

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/bbcode/preview", true);
    xhr.setRequestHeader("Cache-Control", "no-cache");

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            var htmlPreview = xhr.responseText;
            if (!htmlPreview) return;

            var previewContainer = document.createElement('div');
            previewContainer.className = 'bbcode-preview bbcode';
            previewContainer.innerHTML = htmlPreview;

            bbcodeWrapper.appendChild(previewContainer);
        } else {
            var previewContainer = document.createElement('div');
            previewContainer.className = 'bbcode-preview bbcode';
            previewContainer.appendChild(
                document.createTextNode('Failed to load bbcode preview :(')
            );
            bbcodeWrapper.appendChild(previewContainer);
            console.error(xhr.status + ': "' + xhr.statusText + '"');
        }
    };

    xhr.onerror = function() {
        var previewContainer = document.createElement('div');
        previewContainer.className = 'bbcode-preview bbcode';
        previewContainer.appendChild(
            document.createTextNode('Failed to load bbcode preview :(')
        );
        bbcodeWrapper.appendChild(previewContainer);
        console.error('BBCode request failed');
    };

    xhr.send(form);
    return false;
}

function confirmAction(promptText) {
    if (promptText === undefined) promptText = 'Are you sure?';
    return confirm(promptText);
}

function confirmRedirect(url, promptText) {
    var do_redirect = confirmAction(promptText);

    if (!do_redirect)
        return;

    window.location.href = url;
    return false;
}

function cookieExists(name) {
    return document.cookie.indexOf(name + "=") !== -1;
}

function isLoggedIn() {
    return document.getElementById('welcome-text').textContent != 'Welcome, guest!'
}

function show(id) {
    $('#' + id).show();
}

function hide(id) {
    $('#' + id).hide();
}

addEvent("DOMContentLoaded", document, function(event) {
    $(".timeago").timeago();
});

var params = new URLSearchParams(location.search);

if (params.get('wait') && location.pathname == '/') {
    alert('Too many login attempts. Please wait a minute and try again!');
}
