var Mods = {
    NoMod: 0,
    NoFail: 1 << 0,
    Easy: 1 << 1,
    NoVideo: 1 << 2,
    Hidden: 1 << 3,
    HardRock: 1 << 4,
    SuddenDeath: 1 << 5,
    DoubleTime: 1 << 6,
    Relax: 1 << 7,
    HalfTime: 1 << 8,
    Nightcore: 1 << 9,
    Flashlight: 1 << 10,
    Autoplay: 1 << 11,
    SpunOut: 1 << 12,
    Autopilot: 1 << 13,
    Perfect: 1 << 14,
    Key4: 1 << 15,
    Key5: 1 << 16,
    Key6: 1 << 17,
    Key7: 1 << 18,
    Key8: 1 << 19,
    FadeIn: 1 << 20,
    Random: 1 << 21,
    Cinema: 1 << 22,
    Target: 1 << 23,
    Key9: 1 << 24,
    KeyCoop: 1 << 25,
    Key1: 1 << 26,
    Key3: 1 << 27,
    Key2: 1 << 28,
    ScoreV2: 1 << 29,
    Mirror: 1 << 30,
    KeyMod: (1 << 15) | (1 << 16) | (1 << 17) | (1 << 18) | (1 << 19) | (1 << 24) | (1 << 25) | (1 << 26) | (1 << 27) | (1 << 28),
    FreeModAllowed: (1 << 0) | (1 << 1) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 10) | (1 << 20) | (1 << 7) | (1 << 13) | (1 << 12) | (1 << 15) | (1 << 16) | (1 << 17) | (1 << 18) | (1 << 19),
    SpeedMods: (1 << 6) | (1 << 8) | (1 << 9),

    getMembers: function() {
        var memberList = [];
        for (var mod in Mods) {
            if (Object.prototype.hasOwnProperty.call(mod) && Mods[mod] === (Mods[mod] & this[mod])) {
                memberList[memberList.length] = mod;
            }
        }
        return memberList;
    },

    getString: function(value) {
        var modMap = {};
        modMap[Mods.NoMod] = "NM";
        modMap[Mods.NoFail] = "NF";
        modMap[Mods.Easy] = "EZ";
        modMap[Mods.Hidden] = "HD";
        modMap[Mods.HardRock] = "HR";
        modMap[Mods.SuddenDeath] = "SD";
        modMap[Mods.DoubleTime] = "DT";
        modMap[Mods.Relax] = "RX";
        modMap[Mods.HalfTime] = "HT";
        modMap[Mods.Nightcore] = "NC";
        modMap[Mods.Flashlight] = "FL";
        modMap[Mods.Autoplay] = "AT";
        modMap[Mods.SpunOut] = "SO";
        modMap[Mods.Autopilot] = "AP";
        modMap[Mods.Perfect] = "PF";
        modMap[Mods.Key4] = "K4";
        modMap[Mods.Key5] = "K5";
        modMap[Mods.Key6] = "K6";
        modMap[Mods.Key7] = "K7";
        modMap[Mods.Key8] = "K8";

        var members = [];
        for (var mod in Mods) {
            if (Mods.hasOwnProperty(mod) && Mods[mod] !== 0 && (value & Mods[mod]) === Mods[mod]) {
                members[members.length] = mod;
            }
        }

        if (members.indexOf("DT") !== -1 && members.indexOf("NC") !== -1) {
            members.splice(members.indexOf("DT"), 1);
        }

        var result = [];
        for (var i = 0; i < members.length; i++) {
            result[result.length] = modMap[Mods[members[i]]];
        }
        return result.join("");
    }
};

var Mode = {
    0: "osu!",
    1: "Taiko",
    2: "Catch the Beat",
    3: "osu!Mania"
};

var isNavigatingAway = false;
var pageLoaded = false;
var apiRetries = 0;

if (!window.console) {
    // Console polyfill for ~IE8 and earlier
    window.console = {
        log: function() {},
        info: function() {},
        warn: function() {},
        error: function() {}
    };
}

if (!window.FormData) {
    window.FormData = function(form) {};
}

function slideDown(elem) {
    // Use jQuery's slideDown for cross-browser compatibility
    elem.style.height = '';
    $(elem).stop(true, false).slideDown(500);
}

function slideUp(elem) {
    // Use jQuery's slideUp for cross-browser compatibility
    $(elem).stop(true, false).slideUp(500);
    setTimeout(function() { elem.style.height = '0px' }, 500);
}

function isHidden(elem) {
    // Cross-browser compatible check for hidden elements
    return elem.style.display === 'none' || elem.offsetParent === null ||
           elem.offsetWidth === 0 || elem.offsetHeight === 0;
}

function getElementHeight(elem) {
    var totalHeight = 0;
    for (var i = 0; i < elem.children.length; i++) {
        totalHeight += elem.children[i].offsetHeight + 10;
    }
    return totalHeight;
}

function getText(elem) {
    return elem.textContent || elem.innerText;
}

function setText(elem, text) {
    if (elem.textContent !== undefined) {
        elem.textContent = text;
    } else {
        elem.innerText = text;
    }
}

function isLoggedIn() {
    return currentUser !== null;
}

function isArray(obj) {
    return Object.prototype.toString.call(obj) === '[object Array]';
}

function show(id) {
    $('#' + id).show();
}

function hide(id) {
    $('#' + id).hide();
}

function confirmAction(promptText) {
    if (promptText === undefined) promptText = 'Are you sure?';
    return confirm(promptText);
}

function cookieExists(name) {
    return document.cookie.indexOf(name + "=") !== -1;
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function confirmRedirect(url, promptText) {
    var do_redirect = confirmAction(promptText);

    if (!do_redirect)
        return;

    window.location.href = url;
    return false;
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
    var spoiler = $(root).closest(".spoiler");
    spoiler.children(".spoiler-body").slideToggle("fast");
    spoiler.find('img').trigger('unveil');
    return false;
}

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

function performApiRequest(method, path, data, callbackSuccess, callbackError) {    
    var url = apiBaseurl + path;
    var xhr;

    // Use XMLHttpRequest or XDomainRequest if available
    // otherwise, try ActiveX for older IE versions
    try {
        if (window.XDomainRequest) {
            // IE8 and IE9
            xhr = new XDomainRequest();
        } else if (window.XMLHttpRequest) {
            // Modern browsers
            xhr = new XMLHttpRequest();
        } else {
            // IE6 and IE7
            xhr = new ActiveXObject("Microsoft.XMLHTTP");
            // Rewrite url to use /api as fallback, due to cors limitations
            url = osuBaseurl + "/api" + path;
        }
    } catch (e) {
        throw new Error("This browser does not support AJAX requests.");
    }

    try {
        xhr.withCredentials = true;
    } catch (e) {
        console.warn("This browser does not support ajax credentials.");
    }

    // Use the current site protocol
    url = url.replace(/^https?:\/\//, '');
    url = location.protocol + '//' + url

    try {
        // Open the request
        xhr.open(method, url, true);
    } catch (e) {
        if (callbackError) {
            callbackError(xhr);
        }
        console.error("An error occurred while opening the request: " + e);
        return;
    }

    // Determine content type & request data format
    var contentType = null;
    var requestData = data;

    if (data instanceof FormData) {
        contentType = null;
        requestData = data;
    } else if (typeof data === 'object' && data !== null) {
        requestData = JSON.stringify(data);
        contentType = "application/json; charset=UTF-8";
    } else if (typeof data === 'string') {
        contentType = "text/plain; charset=UTF-8";
    }

    try {
        xhr.setRequestHeader("Cache-Control", "no-cache");
        xhr.setRequestHeader("X-CSRF-Token", csrfToken);
        
        if (contentType !== null)
        {
            xhr.setRequestHeader("Content-Type", contentType);
        }

        if (cookieExists('access_token'))
        {
            // Set the Authorization header, if the access_token cookie is accessible via. javascript
            // This will be useful for local development, where the api is located on a different domain
            xhr.setRequestHeader("Authorization", "Bearer " + getCookie('access_token'));
        }
    } catch (e) {
        console.warn("This browser does not support setting headers.");
    }

    if (xhr.onreadystatechange === undefined) {
        xhr.onload = function() {
            apiRetries = 0;
            console.log("Request successful: " + method + " " + path);
            apiRetries = 0;

            if (callbackSuccess) {
                try {
                    callbackSuccess(xhr);
                } catch (e) {
                    console.error("An error occurred while processing the response: " + e);
                    throw e;
                }
            }
        }

        xhr.onerror = function() {
            var retried = handleApiError(
                xhr, method, path, data,
                callbackSuccess, callbackError
            );

            if (retried)
                return;

            console.error("An error occurred during " + method + " request to " + path);
            if (callbackError) {
                callbackError(xhr);
            }
        }

        xhr.send(requestData);
        return xhr;
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4)
            return;

        if (xhr.status >= 200 && xhr.status < 300) {
            console.log("[" + xhr.status + "] Request successful: " + method + " " + path);
            apiRetries = 0;

            if (callbackSuccess) {
                try {
                    callbackSuccess(xhr);
                } catch (e) {
                    console.error("An error occurred while processing the response: " + e);
                    throw e;
                }
            }
        } else {
            var retried = handleApiError(
                xhr, method, path, data,
                callbackSuccess, callbackError
            );

            if (retried)
                return;

            console.error("[" + xhr.status + "] An error occurred during " + method + " request to " + path);
            if (callbackError && !isNavigatingAway) {
                callbackError(xhr);
            }
        }
    };

    xhr.send(requestData);
    return xhr;
}

function handleApiError(xhr, method, path, data, callbackSuccess, callbackError) {
    if (xhr.status !== 403)
        return false;

    if (apiRetries >= 2)
        return false;

    try {
        var response = JSON.parse(xhr.responseText);
        if (!response || response.details !== "Invalid CSRF token")
            return false;

        reloadCsrfToken(function() {
            apiRetries += 1;
            console.log("Retrying " + method + " request to " + path + " after reloading CSRF token");
            performApiRequest(method, path, data, callbackSuccess, callbackError);
        });
        return true;
    } catch (e) {
        console.error("Failed to parse API error response: " + e);
        return false;
    }
}

function convertFormToJson(formElement) {
    var formData = formElement.elements;
    var jsonData = {};

    for (var i = 0; i < formData.length; i++) {
        var field = formData[i];
        var value;

        if (field.name && !field.disabled) {
            if (field.type === "checkbox") {
                if (!field.checked) continue;
                value = field.value !== undefined ? field.value : "on";
            } else if (field.type === "radio") {
                if (!field.checked) continue;
                value = field.value;
            } else {
                value = field.value;
            }

            if (jsonData[field.name] === undefined) {
                jsonData[field.name] = value;
            } else if (isArray(jsonData[field.name])) {
                jsonData[field.name].push(value);
            } else {
                jsonData[field.name] = [jsonData[field.name], value];
            }
        }
    }
    return jsonData;
}

function loadBBCodePreview(element) {
    var parentElement = getParentElement(element);
    var bbcodeWrapper = getParentElement(parentElement);
    var bbcodeEditor = bbcodeWrapper.querySelector('textarea');

    // Remove old previews
    var previews = document.querySelectorAll('.bbcode-preview');
    Array.prototype.forEach.call(previews, function (element) {
        element.parentNode.removeChild(element);
    });

    performApiRequest("POST", "/forum/bbcode", { "input": bbcodeEditor.value }, function(xhr) {
        var htmlPreview = xhr.responseText;
        if (!htmlPreview) return;

        var previewContainer = document.createElement('div');
        previewContainer.className = 'bbcode-preview bbcode';
        previewContainer.innerHTML = htmlPreview;

        bbcodeWrapper.appendChild(previewContainer);
    }, function(xhr) {
        var previewContainer = document.createElement('div');
        previewContainer.className = 'bbcode-preview bbcode';
        previewContainer.appendChild(
            document.createTextNode('Failed to load bbcode preview :(')
        );
        bbcodeWrapper.appendChild(previewContainer);
        console.error(xhr.status + ': "' + xhr.statusText + '"');
    });
    return false;
}

function reloadCsrfToken(callback) {
    performApiRequest("GET", "/account/csrf", null, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        if (response && response.token) {
            csrfToken = response.token;
            applyCsrfToForms();
            if (callback) callback();
        } else {
            console.error("Failed to reload CSRF token: invalid response");
        }
    }, function(xhr) {
        console.error("Failed to reload CSRF token");
    });
}

function applyCsrfToForms() {
    var inputs = $('input[name="csrf_token"]');

    for (var i = 0; i < inputs.length; i++) {
        inputs[i].attributes.value = csrfToken;
    }
}

function reloadCsrfBeforeSubmit(formElement) {
    var submitHandler = function(e) {
        e.preventDefault();
        reloadCsrfToken(function() {
            HTMLFormElement.prototype.submit.call(formElement);
        });
    };

    formElement.addEventListener('submit', submitHandler, false);
}

function applyCsrfUpdaterToForms() {
    var forms = document.getElementsByTagName('form');

    for (var i = 0; i < forms.length; i++) {
        var elements = $(forms[i]).find('input[name="csrf_token"]');
        if (elements.length > 0) {
            reloadCsrfBeforeSubmit(forms[i]);
        }
    }
}

function renderTimeagoElements() {
    var times = document.getElementsByClassName('timeago');
    for (var i = 0; i < times.length; i++) {
        times[i].innerText = jQuery.timeago(times[i].getAttribute('datetime'));
    }
}

function getElementsByClassNamePolyfill(className) {
    var allElements = document.getElementsByTagName('*');
    var matchedElements = [];
    var pattern = new RegExp('(^|\\s)' + className + '(\\s|$)');

    for (var i = 0; i < allElements.length; i++) {
        if (pattern.test(allElements[i].className)) {
            matchedElements.push(allElements[i]);
        }
    }
    return matchedElements;
}

if (!document.getElementsByClassName) {
    document.getElementsByClassName = getElementsByClassNamePolyfill;
}

addEvent("DOMContentLoaded", document, function(e) {
    pageLoaded = true;
    renderTimeagoElements();

    if (isLoggedIn()) {
        applyCsrfUpdaterToForms();
    }
});

addEvent("beforeunload", window, function(e) {
    isNavigatingAway = true;
});

addEvent("visibilitychange", document, function(e) {
    if (!isLoggedIn())
        return;

    if (!pageLoaded)
        return;

    if (document.visibilityState === "visible")
        reloadCsrfToken();
});
