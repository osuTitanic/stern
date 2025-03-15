
from app.common.database import users, notifications, topics
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
        return utils.render_template(
            'settings/overview.html',
            css='settings.css',
            bookmarks=topics.fetch_user_bookmarks(
                flask_login.current_user.id,
                session=session
            ),
            notifications=notifications.fetch_all(
                flask_login.current_user.id,
                read=False,
                session=session
            ),
            total_posts=users.fetch_post_count(
                flask_login.current_user.id,
                session=session
            )
        )
