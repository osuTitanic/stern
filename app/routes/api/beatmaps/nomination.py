
from app.common.database import beatmapsets, nominations, topics

from flask_login import current_user, login_required
from flask import Blueprint, abort, redirect
from flask_pydantic import validate

import app

router = Blueprint('beatmap-nomination', __name__)

@router.get('/nominations/<set_id>/add')
@login_required
@validate()
def add_nomination(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if nominations.fetch_one(set_id, current_user.id, session):
            # User already nominated that map
            return redirect(f'/s/{set_id}')

        nominations.create(
            beatmapset.id,
            current_user.id,
            session=session
        )

        # Set icon to bubble
        topics.update(
            beatmapset.topic_id,
            {'icon_id': 3},
            session=session
        )

    return redirect(f'/s/{set_id}')

@router.get('/nominations/<set_id>/reset')
@login_required
@validate()
def reset_nominations(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        nominations.delete_all(
            beatmapset.id,
            session=session
        )

        # Set icon to popped bubble
        topics.update(
            beatmapset.topic_id,
            {'icon_id': 4},
            session=session
        )

    return redirect(f'/s/{set_id}')
