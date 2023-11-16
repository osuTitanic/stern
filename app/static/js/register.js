function validateField(element)
{
    const type = element.getAttribute("name");
    const value = element.value;

    if (!value)
        return;

    const descriptionField = element.parentElement.querySelector(".input-description");
    descriptionField.textContent = "Checking...";

    fetch(`/account/register/check?type=${type}&value=${value}`)
        .then(response => {
            if (!response.ok) {
                descriptionField.textContent = "Could not verify this field. Please try something else!";
                return;
            }

            return response.text();
        })
        .then(validationError => {
            if (!validationError.length)
            {
                descriptionField.textContent = "Looking good!";
                return;
            }

            descriptionField.textContent = validationError;
        })
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
