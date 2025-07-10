
from flask import Blueprint, abort

import config
import utils

router = Blueprint('events', __name__)

@router.get('/events')
def events_page():
    if not config.DEBUG:
        # Disabled for now, page is under development
        return abort(404)

    return utils.render_template(
        'events.html',
        css='events.css',
        site_title="Activity Feed",
        site_description="Keep up with what's going on in Titanic!",
        websocket_endpoint=config.EVENTS_WEBSOCKET
    )
