
from flask import Blueprint

import flask_login
import utils

router = Blueprint('chat', __name__)

@router.get('/chat')
@flask_login.login_required
def chat_view():
    return utils.render_template(
        'settings/chat.html',
        css='settings.css'
    )
