
from app.common.database import beatmapsets, beatmaps, topics, posts
from app.common.constants import BeatmapLanguage, BeatmapGenre

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required
from flask_pydantic import validate

import hashlib
import app

# TODO: Move hash update & description endpoint to new API

router = Blueprint('beatmap-updates', __name__)
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

        beatmap_topic = topics.fetch_one(
            beatmapset.topic_id,
            session=session
        )

        if not beatmap_topic:
            return redirect(f'/s/{set_id}')

        initial_post = posts.fetch_initial_post(
            beatmap_topic.id,
            session=session
        )

        if not initial_post:
            return redirect(f'/s/{set_id}')

        if '---------------' not in initial_post.content.splitlines():
            return redirect(f'/s/{set_id}')

        metadata, _ = initial_post.content.split('---------------', 1)

        # Update forum topic content with new description
        posts.update(
            initial_post.id,
            {'content': f'{metadata}---------------\n{description}'},
            session=session
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
            return redirect(f'/b/{beatmap.id}')

    return redirect(f'/s/{beatmapset.id}')

@router.post('/update/')
@login_required
def metadata_update():
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
