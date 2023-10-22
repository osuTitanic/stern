var activeTab = window.location.hash != "" ? window.location.hash.replace("#","") : "general";

const slideDown = elem => elem.style.height = `${elem.scrollHeight}px`;
const slideUp = elem => elem.style.height = "0px";

const Mods = {
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
    LastMod: 1 << 29,
    KeyMod: 1 << 15 | 1 << 16 | 1 << 17 | 1 << 18 | 1 << 19,
    SpeedMods: 1 << 6 | 1 << 8 | 1 << 9,
    FreeModAllowed: 1 << 0 | 1 << 1 | 1 << 3 | 1 << 4 | 1 << 5 | 1 << 10 | 1 << 20 | 1 << 7 | 1 << 13 | 1 << 12 | 1 << 15 | 1 << 16 | 1 << 17 | 1 << 18 | 1 << 19,

    getMembers: function() {
      let memberList = [];
      for (const mod in Mods) {
        if (Mods[mod] === (Mods[mod] & this[mod])) {
          memberList.push(mod);
        }
      }
      return memberList;
    },

    getString: function(value) {
      const modMap = {
        [Mods.NoMod]: "NM",
        [Mods.NoFail]: "NF",
        [Mods.Easy]: "EZ",
        [Mods.Hidden]: "HD",
        [Mods.HardRock]: "HR",
        [Mods.SuddenDeath]: "SD",
        [Mods.DoubleTime]: "DT",
        [Mods.Relax]: "RX",
        [Mods.HalfTime]: "HT",
        [Mods.Nightcore]: "NC",
        [Mods.Flashlight]: "FL",
        [Mods.Autoplay]: "AT",
        [Mods.SpunOut]: "SO",
        [Mods.Autopilot]: "AP",
        [Mods.Perfect]: "PF",
        [Mods.Key4]: "K4",
        [Mods.Key5]: "K5",
        [Mods.Key6]: "K6",
        [Mods.Key7]: "K7",
        [Mods.Key8]: "K8",
      };

      const members = [];
      for (const mod in Mods) {
        if (Mods[mod] !== 0 && (value & Mods[mod]) === Mods[mod]) {
          members.push(mod);
        }
      }

      return members.map(mod => modMap[Mods[mod]]).join("");
    }
};

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