
from app.common.database.repositories import groups
from flask import Blueprint, abort

import utils
import app

router = Blueprint('groups', __name__)

@router.get('/<id>')
def get_group(id: int):
    with app.session.database.managed_session() as session:
        if not (group := groups.fetch_one(id, session)):
            return abort(404)

        if group.hidden:
            return abort(404)

        users = groups.fetch_group_users(group.id, session)

        return utils.render_template(
            'group.html',
            css='group.css',
            group=group,
            users=users
        )
