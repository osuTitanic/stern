function displayCategory(category) {
    var clients = document.querySelectorAll(".client-container");

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
    var categoryLinks = document.querySelectorAll(".category");
    deselectAll();

    for (var i = 0; i < categoryLinks.length; i++) {
        var categoryLink = categoryLinks[i];

        if (categoryLink.textContent == category) {
            categoryLink.classList.add('selected');
        } else {
            categoryLink.classList.remove('selected');
        }
    }
}

function deselectCategory(category)
{
    var categoryLinks = document.querySelectorAll(".category");
    
    for (var i = 0; i < categoryLinks.length; i++) {
        var categoryLink = categoryLinks[i];
        
        if (categoryLink.textContent == category) {
            categoryLink.classList.remove('selected');
        }
    }
}

function deselectAll()
{
    var selectedCategories = document.querySelectorAll(".category .selected");

    for (var i = 0; i < selectedCategories.length; i++) {
        selectedCategories[i].classList.remove('selected');
    }
}
