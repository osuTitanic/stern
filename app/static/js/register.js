function validateField(element) {
    var type = element.getAttribute("name");
    var value = element.value;
    var descriptionField = getParentElement(element).querySelector(".input-description");

    if (!value) return;

    descriptionField.textContent = "Checking...";
    descriptionField.style.fontWeight = "normal";

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/account/register/check?type=' + encodeURIComponent(type) + '&value=' + encodeURIComponent(value), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status !== 200) {
                descriptionField.textContent = "Could not verify this field. Please try something else!";
                descriptionField.style.fontWeight = "bold";
                return;
            }

            var validationError = xhr.responseText;
            if (validationError.length === 0) {
                descriptionField.textContent = "Looking good!";
                descriptionField.style.fontWeight = "normal";
            } else {
                descriptionField.textContent = validationError;
                descriptionField.style.fontWeight = "bold";
            }
        }
    };
    xhr.send();
}

function isValid(element) {
    var descriptionField = getParentElement(element).querySelector(".input-description");
    var type = element.getAttribute("name");
    var value = element.value;

    if (!value) {
        descriptionField.textContent = "This field is required!";
        descriptionField.style.fontWeight = "bold";
        return false;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/account/register/check?type=' + encodeURIComponent(type) + '&value=' + encodeURIComponent(value), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status !== 200) {
                descriptionField.textContent = "Could not verify this field. Please try something else!";
                descriptionField.style.fontWeight = "bold";
                return false;
            }

            var validationError = xhr.responseText;
            if (validationError.length > 0) {
                descriptionField.textContent = validationError;
                descriptionField.style.fontWeight = "bold";
                return false;
            }

            descriptionField.textContent = "Looking good!";
            descriptionField.style.fontWeight = "normal";
            return true;
        }
    };
    xhr.send();
    return true; // Assume valid until we receive a response
}

function validateAll(event) {
    event.preventDefault();

    var validationFields = document.querySelectorAll(".validate");
    var promises = [];

    for (var i = 0; i < validationFields.length; i++) {
        (function (field) {
            promises.push(new Promise(function (resolve) {
                isValid(field) && resolve(true);
            }));
        })(validationFields[i]);
    }

    Promise.all(promises).then(function (results) {
        var allValid = results.every(function (valid) {
            return valid;
        });
        if (allValid) {
            event.target.submit();
        }
    });
}

var timeout = null;

var validationFields = document.querySelectorAll(".validate");
for (var j = 0; j < validationFields.length; j++) {
    (function (element) {
        addEvent("keyup", element, function() {
            clearTimeout(timeout);

            timeout = setTimeout(function() {
                validateField(element);
            }, 500);
        });

        addEvent("blur", element, function() {
            validateField(element);
        });
    })(validationFields[j]);
}
