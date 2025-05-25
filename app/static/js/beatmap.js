function addFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites";

    performApiRequest("POST", url, {"set_id": beatmapsetId}, function(xhr) {
        var favourites = document.getElementById('favourites-button');
        favourites.innerHTML = '(Remove Favourite)';
        favourites.style.color = 'red';
        favourites.onclick = function () {
            removeFavorite(beatmapsetId);
        };
    });
}

function removeFavorite(beatmapsetId) {
    var url = "/users/" + currentUser + "/favourites/" + beatmapsetId;

    performApiRequest("DELETE", url, null, function(xhr) {
        var favourites = document.getElementById('favourites-button');
        favourites.innerHTML = '(Add Favourite)';
        favourites.style.color = 'green';
        favourites.onclick = function () {
            addFavorite(beatmapsetId);
        };
    });
}

function copySetId(element) {
    var set_id = element.getAttribute('setid');

    navigator.clipboard.writeText(set_id).then(function () {
        element.innerHTML = 'Copied!';
        element.style.color = 'green';
    }, function () {
        element.innerHTML = 'Failed to copy!';
        element.style.color = 'red';
    });

    setTimeout(function () {
        element.innerHTML = 'Copy Beatmapset ID';
        element.style.color = 'rgb(0, 102, 204)';
    }, 1500);
}

function editBeatmapDescription() {
    var description = document.querySelector('.beatmap-description .bbcode');
    if (!description) { return; }

    var form = document.createElement('form');
    form.action = '/api/beatmaps/update/' + beatmapsetId + '/description';
    form.method = 'post';

    var textarea = document.createElement('textarea');
    textarea.className = 'description-editor bbcode-editor';
    textarea.innerHTML = bbcodeDescription;
    textarea.name = 'description';
    form.appendChild(textarea);

    var csrfTokenInput = document.createElement('input');
    csrfTokenInput.type = 'hidden';
    csrfTokenInput.name = 'csrf_token';
    csrfTokenInput.value = csrfToken;
    form.appendChild(csrfTokenInput);

    var submitButton = document.createElement('input');
    submitButton.type = 'submit';
    submitButton.value = 'Save';
    form.appendChild(submitButton);

    description.replaceWith(form);
}

function convertBanchoSpoilerBoxes() {
    // osu.ppy.sh spoilerbox conversion
    var spoilerBoxes = document.querySelectorAll('.bbcode-spoilerbox');
    for (var i = 0; i < spoilerBoxes.length; i++) {
        spoilerBoxes[i].classList.add('spoiler');
    }

    var spoilerBoxContents = document.querySelectorAll('.bbcode-spoilerbox__body');
    for (var i = 0; i < spoilerBoxContents.length; i++) {
        spoilerBoxContents[i].classList.add('spoiler-body');
    }

    var spoilerBoxHeads = document.querySelectorAll('.bbcode-spoilerbox__link');
    for (var i = 0; i < spoilerBoxHeads.length; i++) {
        var spoilerBox = spoilerBoxHeads[i];
        
        // Change element type to div (in older versions of Chrome, use workarounds if necessary)
        var newSpoilerBox = document.createElement('div');
        newSpoilerBox.className = spoilerBox.className + ' spoiler-head';
        newSpoilerBox.innerHTML = spoilerBox.innerHTML;
        spoilerBox.parentNode.replaceChild(newSpoilerBox, spoilerBox);
        
        newSpoilerBox.onclick = function () {
            toggleSpoiler(this);
        };
    }
}

function setBeatmapVolume(volume) {
    var beatmapPreview = document.getElementById('beatmap-preview');
    if (beatmapPreview) {
        beatmapPreview.volume = volume;
    }
}

addEvent('DOMContentLoaded', document, function() {
    var url = window.location.pathname;
    if (!url.startsWith('/b/') && !url.startsWith('/s/')) {
        return;
    }

    convertBanchoSpoilerBoxes();
    setBeatmapVolume(0.5);

    if (!isBeatmapsetOwner) {
        return;
    }

    var descriptionElements = document.querySelectorAll('.beatmap-description, .beatmap-description *');

    for (var i = 0; i < descriptionElements.length; i++) {
        addEvent('dblclick', descriptionElements[i], function(event) {
            editBeatmapDescription();
        });
    }
});