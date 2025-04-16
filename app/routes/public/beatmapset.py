
from app.common.database.repositories import beatmapsets
from flask import Blueprint, abort, redirect, request

import utils
import app

router = Blueprint('beatmapset', __name__)

@router.get('/<id>')
def get_beatmapset(id: int):
    if not id.isdigit():
        return utils.render_error(404, 'beatmap_not_found')

    with app.session.database.managed_session() as session:
        if not (set := beatmapsets.fetch_one(id, session=session)):
            return utils.render_error(404, 'beatmap_not_found')

        if not set.beatmaps:
            return utils.render_error(404, 'beatmap_not_found')

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
