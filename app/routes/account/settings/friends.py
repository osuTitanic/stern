
from app.common.database.repositories import relationships
from flask import Blueprint

import flask_login
import utils
import app

router = Blueprint('friend-settings', __name__)

@router.get('/friends')
@flask_login.login_required
def manage_friends():
    with app.session.database.managed_session() as session:
        return utils.render_template(
            'settings/friends.html',
            css='settings.css',
            session=session,
            friends=relationships.fetch_users(
                flask_login.current_user.id,
                session=session
            )
        )
