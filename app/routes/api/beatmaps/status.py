
from app.common.constants import DatabaseStatus
from app.common.database import DBBeatmapset
from app.common.database import (
    nominations,
    beatmapsets,
    beatmaps,
    topics,
    posts
)

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required
from sqlalchemy.orm import Session
from datetime import datetime

import utils
import app

router = Blueprint('beatmap-status', __name__)

def has_enough_nominations(beatmapset: DBBeatmapset, session: Session) -> bool:
    count = nominations.count(
        beatmapset.id,
        session=session
    )

    return count >= utils.required_nominations(beatmapset)

def move_beatmap_topic(beatmapset: DBBeatmapset, status: int, session: Session):
    if not beatmapset.topic_id:
        return

    if status > DatabaseStatus.Pending:
        topics.update(
            beatmapset.topic_id,
            {'forum_id': 8},
            session=session
        )
        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 8},
            session=session
        )

    elif status == DatabaseStatus.WIP:
        topics.update(
            beatmapset.topic_id,
            {'forum_id': 10},
            session=session
        )
        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 10},
            session=session
        )

    else:
        topics.update(
            beatmapset.topic_id,
            {'forum_id': 9},
            session=session
        )
        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 9},
            session=session
        )

@router.post('/status/difficulty')
@login_required
def diff_status_update():
    if not current_user.is_bat:
        return abort(code=401)

    if not (set_id := request.form.get('beatmapset_id')):
        return abort(code=400)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        statuses = {
            int(key.removeprefix('status-')): int(value)
            for key, value in request.form.items()
            if key.startswith('status')
        }

        if not statuses:
            return abort(code=400)

        set_status = max(statuses.values())

        contains_ranked_status = any(
            status == DatabaseStatus.Ranked
            for status in statuses.values()
        )

        if contains_ranked_status:
            if beatmapset.status not in (DatabaseStatus.Ranked, DatabaseStatus.Approved):
                return redirect(
                    f'/b/{list(statuses.keys())[0]}?bat_error=This beatmap is not yet ranked. Try to qualify it first!'
                )

            set_status = DatabaseStatus.Ranked.value

        contains_approved_status = any(
            status == DatabaseStatus.Approved
            for status in statuses.values()
        )

        if contains_approved_status:
            if not has_enough_nominations(beatmapset, session):
                return redirect(
                    f'/b/{list(statuses.keys())[0]}?bat_error=This beatmap has not enough nominations.'
                )

            set_status = DatabaseStatus.Approved.value

        contains_qualified_status = any(
            status == DatabaseStatus.Qualified
            for status in statuses.values()
        )

        if contains_qualified_status:
            if not has_enough_nominations(beatmapset, session):
                return redirect(
                    f'/b/{list(statuses.keys())[0]}?bat_error=This beatmap has not enough nominations.'
                )

            set_status = DatabaseStatus.Qualified.value

        for beatmap_id, status in statuses.items():
            beatmaps.update(
                beatmap_id,
                {'status': status},
                session=session
            )

        beatmapsets.update(
            beatmapset.id,
            {'status': set_status},
            session=session
        )

        move_beatmap_topic(
            beatmapset,
            set_status,
            session=session
        )

        if set_status > DatabaseStatus.Pending:
            beatmapsets.update(
                beatmapset.id,
                {
                    'approved_at': datetime.now(),
                    'approved_by': current_user.id
                },
                session=session
            )

    return redirect(f'/s/{set_id}')
