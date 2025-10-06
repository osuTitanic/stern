function setBeatmapsetStatus(beatmapsetId, status, promptText) {
    if (promptText === undefined) {
        promptText = "Are you sure?";
    }

    if (!confirm(promptText)) {
        return;
    }

    performApiRequest("PATCH", "/beatmapsets/" + beatmapsetId + "/status?status=" + status, null, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function updateBeatmapsetMetadata(event) {
    event.preventDefault();

    var data = convertFormToJson(event.target);
    var url = "/beatmapsets/" + data.beatmapset_id;

    performApiRequest("PATCH", url, data, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function updateBeatmapStatuses(event) {
    event.preventDefault();

    var data = convertFormToJson(event.target);
    var url = "/beatmapsets/" + data.beatmapset_id + "/status/beatmaps";

    performApiRequest("PATCH", url, data, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function nukeBeatmapset(beatmapsetId) {
    if (!confirm("This will fully delete the beatmap, are you sure you want to proceed?")) {
        return;
    }

    performApiRequest("POST", "/beatmapsets/" + beatmapsetId + "/nuke", null, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function addNomination(beatmapsetId) {
    var url = "/beatmapsets/" + beatmapsetId + "/nominations";

    performApiRequest("POST", url, null, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function resetNominations(beatmapsetId) {
    if (!confirm("This will remove all nominations from this beatmap, are you sure you want to proceed?")) {
        return;
    }

    var url = "/beatmapsets/" + beatmapsetId + "/nominations";

    performApiRequest("DELETE", url, null, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}

function uploadResource(endpoint, key, filetypes, promptText) {
    var fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = filetypes;

    fileInput.onchange = function(event) {
        var file = event.target.files[0];
        if (!file) {
            return;
        }

        if (promptText === undefined) {
            promptText = "Are you sure?";
        }

        if (!confirm(decodeURI(promptText))) {
            return;
        }

        // Create a FormData object to hold the file
        var formData = new FormData();
        formData.append(key, file, file.name);

        // Perform the API request to upload the file
        performApiRequest("PUT", endpoint, formData, function(xhr) {
            location.reload();
        }, function(xhr) {
            var response = JSON.parse(xhr.responseText);
            alert(response.details);
        });
    };

    // Trigger the file input dialog
    fileInput.click();
}

function updateBeatmapsetOwner(beatmapsetId) {
    var newOwner = prompt("Enter the user ID of the new owner:");

    if (!newOwner || isNaN(newOwner))
        return;

    var url = "/beatmapsets/" + beatmapsetId + "/owner";
    var data = { user_id: newOwner };

    performApiRequest("PATCH", url, data, function(xhr) {
        location.reload();
    }, function(xhr) {
        var response = JSON.parse(xhr.responseText);
        alert(response.details);
    });
}