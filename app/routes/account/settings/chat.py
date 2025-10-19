
from flask import Blueprint, redirect

import flask_login
import utils
import app

router = Blueprint('chat', __name__)

@router.get('/chat')
@flask_login.login_required
def chat_view():
    with app.session.database.managed_session() as session:
        return utils.render_template(
            'settings/chat.html',
            css='settings.css',
            session=session
        )
