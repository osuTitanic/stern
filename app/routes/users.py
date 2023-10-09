
from app.common.database.repositories import users
from flask import Blueprint, abort

import utils

router = Blueprint('users', __name__)

@router.get('/<query>')
def userpage(query: str):
    if not query.isdigit():
        user = users.fetch_by_name_extended(query)
    else:
        user = users.fetch_by_id(int(query))

    if not user:
        raise abort(404)

    return utils.render_template(
        'user.html',
        user=user
    )
