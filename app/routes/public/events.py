
from flask import Blueprint, abort

import config
import utils

router = Blueprint('events', __name__)

@router.get('/events')
def events_page():
    return utils.render_template(
        'events.html',
        css='events.css',
        site_title="Activity Feed",
        site_description="Keep up with what's going on in Titanic!",
        site_image=f"{config.OSU_BASEURL}/images/logo/main-low.png",
        websocket_endpoint=config.EVENTS_WEBSOCKET
    )
