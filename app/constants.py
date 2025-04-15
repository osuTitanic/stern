
from werkzeug.exceptions import NotFound, InternalServerError

NotFound.html_description = (
    '<h1>We could not find what you are looking for...</h1>'
)

InternalServerError.html_description = (
    '<div style="text-align: center">'
    '<h1>Internal Server Error</h1>'
    '<p>Hmm.. I guess something went wrong, huh?</p>'
    '<p>'
    'Either the server is dying or you are trying to break something, whether it was intentional or not. '
    'Or maybe contabo is just trolling us again. Who knows? '
    'Anyway, please try again later or contact the server administrator.'
    '</p>'
    '</div>'
)

BEATMAP_NOT_FOUND = (
    '<h1>The beatmap you are looking for was not found!</h1>'
    'There are a few possible reasons for this:'
    '<ul>'
    '<li>The user may have deleted the map.</li>'
    '<li>The map may only be available on <a onclick="redirectToBancho()">the official osu! website</a>.</li>'
    '<li>The map may have been removed due to infringing content.</li>'
    '<li>You may have made a typo!</li>'
    '</ul>'
)

FORUM_NOT_FOUND = (
    '<h1>The forum you are looking for was not found!</h1>'
    'There are a few possible reasons for this:'
    '<ul>'
    '<li>The forum does not exist.</li>'
    '<li>The forum may have been removed by an admin.</li>'
    '<li>You may have made a typo!</li>'
    '</ul>'
)

TOPIC_NOT_FOUND = (
    '<h1>The topic you are looking for was not found!</h1>'
    'There are a few possible reasons for this:'
    '<ul>'
    '<li>The topic does not exist.</li>'
    '<li>The topic may have been deleted.</li>'
    '<li>You may have made a typo!</li>'
    '</ul>'
)

TOPIC_LOCKED = (
    '<h1>The topic you are trying to post in is locked!</h1>'
)

POST_NOT_FOUND = (
    '<h1>The post you are looking for was not found!</h1>'
    'There are a few possible reasons for this:'
    '<ul>'
    '<li>The post does not exist.</li>'
    '<li>The post may have been deleted.</li>'
    '<li>You may have made a typo!</li>'
    '</ul>'
)

POST_LOCKED = (
    '<h1>The post you are trying to edit is locked!</h1>'
)

USER_SILENCED = (
    '<h1>You are not allowed to make posts while silenced.</h1>'
)

USER_RESTRICTED = (
    '<h1>You are not allowed to make posts while restricted.</h1>'
)

POST_TOO_LONG = (
    '<h1>Your post is too long!</h1>'
    'Please limit your post to 15000 characters or less.'
)

ACHIEVEMENTS = {
    'beatmap-packs': ['Anime Pack vol.1', 'Anime Pack vol.2', 'Anime Pack vol.3', 'Anime Pack vol.4', 'Internet! Pack vol.1', 'Internet! Pack vol.2', 'Internet! Pack vol.3', 'Internet! Pack vol.4', 'Rhythm Game Pack vol.1', 'Rhythm Game Pack vol.2', 'Rhythm Game Pack vol.3', 'Rhythm Game Pack vol.4', 'Video Game Pack vol.1', 'Video Game Pack vol.2', 'Video Game Pack vol.3', 'Video Game Pack vol.4'],
    'dedication': ['5,000 Plays (osu! mode)', '15,000 Plays (osu! mode)', '25,000 Plays (osu! mode)', '50,000 Plays (osu! mode)', '30,000 Drum Hits', '300,000 Drum Hits', '3,000,000 Drum Hits', 'Catch 20,000 fruits', 'Catch 200,000 fruits', 'Catch 2,000,000 fruits', '40,000 Keys', '400,000 Keys', '4,000,000 Keys'],
    'hush-hush': ['A meganekko approaches', 'Challenge Accepted', 'Consolation Prize', "Don't let the bunny distract you!", 'Jack of All Trades', 'Jackpot', 'Most Improved', 'Non-stop Dancer', 'Nonstop', 'Obsessed', 'Quick Draw', 'S-Ranker', 'Stumbler'],
    'skill': ['500 Combo  (any song)', '750 Combo  (any song)', '1000 Combo  (any song)', '2000 Combo  (any song)', 'I can see the top', 'The gradual rise', 'Scaling up', 'Approaching the summit']
}
