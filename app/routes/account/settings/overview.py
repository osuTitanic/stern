
from app.common.database import users, logins, notifications

from datetime import datetime, timedelta
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
            logins=logins.fetch_many(
               flask_login.current_user.id,
               limit=5
            ),
            total_posts=users.fetch_post_count(
                flask_login.current_user.id
            ),
            notifications=new_notifications
        )
