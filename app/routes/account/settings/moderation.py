
from flask_login import login_required, current_user
from flask import Blueprint, redirect, request
from app.common.helpers import permissions
from app.common.database import users
from datetime import datetime

import utils
import app

router = Blueprint('moderation', __name__)

@router.get('/moderation')
@login_required
def user_moderation_panel():
    if not permissions.has_permission('users.moderation', current_user.id):
        return redirect('/account/settings/profile')
    
    return utils.render_template(
        'settings/moderation.html',
        css='settings.css'
    )

@router.get('/moderation/<user_id>')
@login_required
def user_moderation_panel_with_user(user_id: int):
    if not permissions.has_permission('users.moderation', current_user.id):
        return redirect('/account/settings/profile')
    
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return utils.render_error(404, 'user_not_found')

        return utils.render_template(
            'settings/moderation.html',
            css='settings.css',
            session=session,
            user=user
        )
