function validateField(element)
{
    const type = element.getAttribute("name");
    const value = element.value;

    const descriptionField = element.parentElement.querySelector(".input-description");

    if (!value)
        return;

    descriptionField.textContent = "Checking...";
    descriptionField.style.fontWeight = "normal";

    fetch(`/account/register/check?type=${type}&value=${value}`)
        .then(response => {
            if (!response.ok) {
                descriptionField.textContent = "Could not verify this field. Please try something else!";
                descriptionField.style.fontWeight = "bold";
                return;
            }

            return response.text();
        })
        .then(validationError => {
            if (!validationError.length)
            {
                descriptionField.textContent = "Looking good!";
                descriptionField.style.fontWeight = "normal";
                return;
            }

            descriptionField.textContent = validationError;
            descriptionField.style.fontWeight = "bold";
        })
}

async function isValid(element)
{
    const descriptionField = element.parentElement.querySelector(".input-description");
    const type = element.getAttribute("name");
    const value = element.value;

    if (!value)
    {
        descriptionField.textContent = "This field is required!"
        descriptionField.style.fontWeight = "bold";
        return false;
    }

    return fetch(`/account/register/check?type=${type}&value=${value}`)
        .then(response => {
            if (!response.ok)
            {
                descriptionField.textContent = "Could not verify this field. Please try something else!";
                descriptionField.style.fontWeight = "bold";
                return false;
            }

            return response.text();
        })
        .then(validationError => {
            if (validationError.length > 0)
            {
                descriptionField.textContent = validationError;
                descriptionField.style.fontWeight = "bold";
                return false;
            }

            descriptionField.textContent = "Looking good!";
            descriptionField.style.fontWeight = "normal";
            return true;
        })
}

async function validateAll(event)
{
    event.preventDefault();

    const validationFields = document.querySelectorAll(".validate");

    for (var i = 0; i < validationFields.length; i++) {
        var valid = await isValid(validationFields[i])

        if (!valid)
            // TODO: Add some kind of feedback...
            return false;
    }

    event.target.submit();
    return true;
}

var timeout = null;

document.querySelectorAll(".validate").forEach((element) => {
    // Event listener for search query input
    element.addEventListener("keyup", (e) => {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            validateField(element);
        }, 800);
    });
})