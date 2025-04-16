
from app.common.database import beatmapsets, beatmaps
from flask_login import current_user, login_required
from flask import Blueprint, abort, redirect
from flask_pydantic import validate

import hashlib
import app

router = Blueprint('beatmap-updates', __name__)

# TODO: Move hash update endpoint to new API
@router.get('/update/<set_id>/hashes')
@login_required
def update_hashes(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if beatmapset.server != 0:
            return abort(code=400)

        try:
            for beatmap in beatmapset.beatmaps:
                beatmap_file = app.session.storage.get_beatmap(beatmap.id)

                if not beatmap_file:
                    continue

                beatmaps.update(
                    beatmap.id,
                    updates={'md5': hashlib.md5(beatmap_file).hexdigest()},
                    session=session
                )
        except Exception as e:
            app.session.logger.warning(f'Failed to update hashes: {e}')
            return redirect(f'/b/{beatmap.id}?bat_error=Failed to update beatmap hashes.')

    return redirect(f'/s/{beatmapset.id}')

@router.post('/update/')
@login_required
def metadata_update():
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.post('/update/<set_id>/description')
@login_required
@validate()
def update_description(set_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
