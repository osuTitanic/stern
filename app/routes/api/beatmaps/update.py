
from app.common.constants import BeatmapLanguage, BeatmapGenre
from app.common.database.repositories import beatmapsets

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required

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

    return redirect(f'/s/{set_id}')
