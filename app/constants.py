
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
