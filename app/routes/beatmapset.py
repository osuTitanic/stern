
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

    beatmap = set.beatmaps[0]

    # Redirect to beatmap based on mode
    available_beatmaps = [
        map for map in set.beatmaps
        if map.mode == request.args.get('mode', 0, type=int)
    ]

    if available_beatmaps:
       beatmap = available_beatmaps[0]

    return redirect(f'/b/{beatmap.id}{mode}')
