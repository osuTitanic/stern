var activeTab = window.location.hash != "" ? window.location.hash.replace("#","") : "general";

const slideDown = elem => elem.style.height = `${elem.scrollHeight}px`;
const slideUp = elem => elem.style.height = "0px";

function expandProfileTab(id, forceExpand)
{
    var tab = document.getElementById(id);
    activeTab = id;

    console.log(tab.height);

    if (!tab.classList.contains("expanded") || forceExpand)
    {
        tab.classList.add("expanded");
        tab.style.display = "block";

        if (tab.style.height == "0px")
            slideDown(tab);

        if (forceExpand)
            window.location.hash = "#" + activeTab;
    }
    else
    {
        slideUp(tab);
        tab.classList.remove("expanded");
        tab.addEventListener("transitionend", () => {
            tab.style.display = "none";
        }, { once: true })
    }
}

function expandRecentActivity()
{
    document.getElementById("profile-recent-preview").style.display = "none";
    document.getElementById("profile-recent-full").style.display = "block";
    slideDown(document.getElementById("general"));
}