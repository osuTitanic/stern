
from app.common.database.repositories import logins, notifications

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

        old_notifications = notifications.fetch_all(
            flask_login.current_user.id,
            until=datetime.now() - timedelta(days=7),
            read=True,
            session=session
        )

        all_notifications = [*new_notifications, *old_notifications]
        all_notifications.sort(key=lambda n: n.time, reverse=True)

        return utils.render_template(
            'settings/overview.html',
            css='settings.css',
            logins=logins.fetch_many(
               flask_login.current_user.id,
               limit=5
            ),
            notifications=all_notifications
        )
