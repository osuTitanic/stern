
from app.common.database.repositories import groups
from flask import Blueprint, abort

import utils
import app

router = Blueprint('groups', __name__)

@router.get('/<id>')
def get_group(id: str):
    if not id.isdigit():
        return abort(404)

    with app.session.database.managed_session() as session:
        if not (group := groups.fetch_one(int(id), session)):
            return abort(404)

        if group.hidden:
            return abort(404)

        users = groups.fetch_group_users(group.id, session)

        return utils.render_template(
            'group.html',
            css='group.css',
            group=group,
            users=users,
            session=session,
            title=f"{group.name} - Group Info",
            site_title=f"{group.name} - Titanic!",
            site_description=group.description,
            site_image=f"{app.config.OSU_BASEURL}/images/logo/main-low.png",
        )
