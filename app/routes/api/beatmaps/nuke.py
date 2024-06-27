
from app.common.database import beatmapsets, topics, posts, beatmaps
from app.common.constants import DatabaseStatus

from flask_login import current_user, login_required
from flask import Blueprint, abort, redirect

import app

router = Blueprint('beatmap-nuking', __name__)

@router.get('/<set_id>/nuke')
@login_required
def nuke_beatmap(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if not beatmapset.topic_id:
            return redirect(f'/s/{set_id}')

        if beatmapset.status > 0:
            return abort(code=400)

        if not (topic := topics.fetch_one(beatmapset.topic_id, session)):
            return redirect(f'/s/{set_id}')

        topics.update(
            topic.id,
            {
                'icon_id': 7,
                'forum_id': 10
            },
            session=session
        )

        posts.update_by_topic(
            topic.id,
            {'forum_id': 10},
            session=session
        )

        beatmapsets.update(
            set_id,
            {'status': DatabaseStatus.WIP.value},
            session=session
        )

        beatmaps.update_by_set_id(
            set_id,
            {'status': DatabaseStatus.WIP.value},
            session=session
        )

        app.session.logger.info(
            f'Beatmap "{beatmapset.full_name}" was nuked by {current_user.name}.'
        )

    return redirect(f'/s/{set_id}')
