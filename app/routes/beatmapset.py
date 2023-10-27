
from app.common.database.repositories import beatmapsets
from flask import Blueprint, abort, redirect, request

import app

router = Blueprint('beatmapset', __name__)

@router.get('/<id>')
def get_beatmapset(id: int):
    if not id.isdigit():
        return abort(
            code=404,
            description=app.constants.BEATMAP_NOT_FOUND
        )

    if not (set := beatmapsets.fetch_one(id)):
        return abort(
            code=404,
            description=app.constants.BEATMAP_NOT_FOUND
        )

    if mode := request.args.get('mode', ''):
        mode = f'?mode={mode}'

    return redirect(f'/b/{set.beatmaps[0].id}{mode}')
