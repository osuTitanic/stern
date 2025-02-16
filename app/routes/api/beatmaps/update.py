
from app.common.constants import BeatmapLanguage, BeatmapGenre
from app.common.database import beatmapsets, beatmaps

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required
from flask_pydantic import validate

import hashlib
import app

router = Blueprint('beatmap-updates', __name__)

@router.post('/update/')
@login_required
def bat_update():
    if not current_user.is_bat:
        return abort(code=401)

    if not (set_id := request.form.get('beatmapset_id')):
        return abort(code=400)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        global_offset = request.form.get('offset', 0, type=int)
        tags = request.form.get('tags', '')

        language_id = request.form.get('language', type=int) or 1
        genre_id = request.form.get('genre', type=int) or 1

        display_title = (
            request.form.get('display_title')
            or f"[bold:0,size:20]{beatmapset.artist}|[]{beatmapset.title}"
        )

        if language_id not in BeatmapLanguage.values():
            return abort(code=400)
        
        if genre_id not in BeatmapGenre.values():
            return abort(code=400)

        beatmapsets.update(
            beatmapset.id,
            {
                'offset': global_offset,
                'display_title': display_title,
                'language_id': language_id,
                'genre_id': genre_id,
                'tags': tags
            },
            session=session
        )

        app.session.logger.info(
            f'{current_user.name} updated beatmap metadata for "{beatmapset.full_name}".'
        )

    return redirect(f'/s/{set_id}')

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

@router.post('/update/<set_id>/description')
@login_required
@validate()
def update_description(set_id: int):
    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if current_user.id != beatmapset.creator_id:
            return redirect(f'/s/{set_id}')

        description = request.form.get('description', '')

        beatmapsets.update(
            beatmapset.id,
            {'description': description},
            session=session
        )

        app.session.logger.info(
            f'{current_user.name} updated description for "{beatmapset.full_name}".'
        )

    return redirect(f'/s/{set_id}')
