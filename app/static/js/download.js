function displayCategory(category) {
    var clients = document.getElementsByClassName("client-container");

    for (var i = 0; i < clients.length; i++) {
        var client = clients[i];
        var wasEnabled = client.style.display == 'block';

        if (wasEnabled && client.id == category) {
            client.style.display = 'none';
            deselectCategory(category);
            return;
        }

        if (client.id == category) {
            client.style.display = 'block';
        } else {
            client.style.display = 'none';
        }
    }

    selectCategory(category);
}

function selectCategory(category)
{
    var categoryLinks = document.getElementsByClassName("category");

    for (var i = 0; i < categoryLinks.length; i++) {
        var categoryLink = categoryLinks[i];

        if (getText(categoryLink) == category) {
            categoryLink.className = 'category selected';
        } else {
            categoryLink.className = 'category';
        }
    }
}

function deselectCategory(category)
{
    var categoryLinks = document.getElementsByClassName("category");
    
    for (var i = 0; i < categoryLinks.length; i++) {
        var categoryLink = categoryLinks[i];
        
        if (getText(categoryLink) == category) {
            categoryLink.className = 'category';
        }
    }
}

function deselectAll()
{
    var categoryLinks = document.getElementsByClassName("category");

    for (var i = 0; i < categoryLinks.length; i++) {
        var selectedElements = categoryLinks[i].getElementsByClassName("selected")

        for (var j = 0; j < selectedElements.length; j++) {
            selectedElements[j].className = 'category';
        }
    }
}
