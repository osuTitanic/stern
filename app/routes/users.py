
from flask import Blueprint, abort, redirect, request
from app.common.database.repositories import users

import utils

router = Blueprint('users', __name__)

@router.get('/<query>')
def userpage(query: str):
    if not query.isdigit():
        user = users.fetch_by_name_extended(query)

        if not user:
            abort(404)

        return redirect(f'/u/{user.id}')

    if not (user := users.fetch_by_id(int(query))):
        raise abort(404)

    if not (mode := request.args.get('m')):
        mode = user.preferred_mode

    return utils.render_template(
        name='user.html',
        user=user,
        css='user.css',
        mode=mode
    )
