
from app.common.database import users, notifications
from flask_login import login_required
from flask import Blueprint

import flask_login
import utils
import app

router = Blueprint('overview', __name__)

@router.get('/')
@login_required
def settings_overview():
    with app.session.database.managed_session() as session:
        new_notifications = notifications.fetch_all(
            flask_login.current_user.id,
            read=False,
            session=session
        )

        return utils.render_template(
            'settings/overview.html',
            css='settings.css',
            notifications=new_notifications,
            total_posts=users.fetch_post_count(
                flask_login.current_user.id
            )
        )
