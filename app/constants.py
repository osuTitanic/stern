
from werkzeug.exceptions import NotFound

NotFound.description = (
    '<h1>We could not find what you are looking for...</h1>'
)

BEATMAP_NOT_FOUND = (
    '<h1>The beatmap you are looking for was not found!</h1>'
    'There are a few possible reasons for this:'
    '<ul>'
    '<li>The user may have deleted the map.</li>'
    '<li>The map may have been removed due to infringing content.</li>'
    '<li>You may have made a typo!</li>'
    '</ul>'
)

ACHIEVEMENTS = {
    'beatmap-packs': ['Rhythm Game Pack vol.3', 'Video Game Pack vol.3', 'Internet! Pack vol.3', 'Internet! Pack vol.4', 'Rhythm Game Pack vol.2', 'Anime Pack vol.1', 'Internet! Pack vol.2', 'Anime Pack vol.4', 'Anime Pack vol.3', 'Video Game Pack vol.2', 'Rhythm Game Pack vol.1', 'Internet! Pack vol.1', 'Rhythm Game Pack vol.4', 'Video Game Pack vol.4', 'Video Game Pack vol.1', 'Anime Pack vol.2'],
    'dedication': ['400,000 Keys', '300,000 Drum Hits', 'Catch 2,000,000 fruits', '30,000 Drum Hits', '5,000 Plays (osu! mode)', '25,000 Plays (osu! mode)', 'Catch 20,000 fruits', '50,000 Plays (osu! mode)', '15,000 Plays (osu! mode)', '40,000 Keys', '3,000,000 Drum Hits', 'Catch 200,000 fruits', '4,000,000 Keys'],
    'hush-hush': ["Don't let the bunny distract you!", 'Non-stop Dancer', 'Jackpot', 'Jack of All Trades', 'Consolation Prize', 'A meganekko approaches', 'Challenge Accepted', 'Stumbler', 'Obsessed', 'Nonstop', 'Quick Draw', 'Most Improved', 'S-Ranker'],
    'skill': ['2000 Combo  (any song)', 'Scaling up', 'The gradual rise', 'Approaching the summit', 'I can see the top', '500 Combo  (any song)', '1000 Combo  (any song)', '750 Combo  (any song)']
}
