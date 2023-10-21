
function setGameMode(mode)
{
    document.getElementsByClassName("active-mode")[0].classList.remove("active-mode");
    document.getElementById(`gm-${mode}`).classList.add("active-mode");
}
