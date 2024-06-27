
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

    elif status == DatabaseStatus.Graveyard:
        topics.update(
            beatmapset.topic_id,
            {'forum_id': 12},
            session=session
        )
        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 12},
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

def update_beatmap_icon(
    beatmapset: DBBeatmapset,
    status: int,
    previous_status: int,
    session: Session
) -> None:
    if status in (DatabaseStatus.Ranked, DatabaseStatus.Qualified, DatabaseStatus.Loved):
        # Set icon to heart
        topics.update(
            beatmapset.topic_id,
            {'icon_id': 1},
            session=session
        )
        return

    if status == DatabaseStatus.Approved:
        # Set icon to flame
        topics.update(
            beatmapset.topic_id,
            {'icon_id': 5},
            session=session
        )
        return

    ranked_statuses = (
        DatabaseStatus.Qualified,
        DatabaseStatus.Approved,
        DatabaseStatus.Ranked,
        DatabaseStatus.Loved
    )

    if previous_status in ranked_statuses:
        # Set icon to broken heart
        topics.update(
            beatmapset.topic_id,
            {'icon_id': 2},
            session=session
        )
        return

    # Remove icon
    topics.update(
        beatmapset.topic_id,
        {'icon_id': None},
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
            and int(value) != -3
        }

        if not statuses:
            return abort(code=400)

        set_status = max(statuses.values())
        previous_status = beatmapset.status

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

        update_beatmap_icon(
            beatmapset,
            set_status,
            previous_status,
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

        else:
            beatmapsets.update(
                beatmapset.id,
                {
                    'approved_at': None,
                    'approved_by': None
                },
                session=session
            )

        app.session.logger.info(
            f'{current_user.name} updated statuses for "{beatmapset.full_name}".'
        )

    return redirect(f'/s/{set_id}')

def handle_pending_status(beatmapset: DBBeatmapset, session: Session):
    if beatmapset.status > 0:
        nominations.delete_all(
            beatmapset.id,
            session=session
        )

    update_beatmap_icon(
        beatmapset,
        DatabaseStatus.Pending.value,
        beatmapset.status,
        session=session
    )

    beatmapsets.update(
        beatmapset.id,
        {
            'status': DatabaseStatus.Pending.value,
            'approved_at': None,
            'approved_by': None
        },
        session=session
    )

    beatmaps.update_by_set_id(
        beatmapset.id,
        {'status': DatabaseStatus.Pending.value},
        session=session
    )

    move_beatmap_topic(
        beatmapset,
        DatabaseStatus.Pending.value,
        session=session
    )

    app.session.logger.info(
        f'"{beatmapset.full_name}" was set to "Pending" status by {current_user.name}.'
    )

    return redirect(
        f'/s/{beatmapset.id}'
    )

def handle_approved_status(beatmapset: DBBeatmapset, session: Session):
    if not has_enough_nominations(beatmapset, session):
        return redirect(
            f'/b/{beatmapset.beatmaps[0].id}?bat_error=This beatmap has not enough nominations.'
        )

    update_beatmap_icon(
        beatmapset,
        DatabaseStatus.Approved.value,
        beatmapset.status,
        session=session
    )

    beatmapsets.update(
        beatmapset.id,
        {
            'status': DatabaseStatus.Approved.value,
            'approved_at': datetime.now(),
            'approved_by': current_user.id
        },
        session=session
    )

    beatmaps.update_by_set_id(
        beatmapset.id,
        {'status': DatabaseStatus.Approved.value},
        session=session
    )

    move_beatmap_topic(
        beatmapset,
        DatabaseStatus.Approved.value,
        session=session
    )

    app.session.logger.info(
        f'"{beatmapset.full_name}" was set to "Approved" status by {current_user.name}.'
    )

    return redirect(
        f'/s/{beatmapset.id}'
    )

def handle_qualified_status(beatmapset: DBBeatmapset, session: Session):
    if not has_enough_nominations(beatmapset, session):
        return redirect(
            f'/b/{beatmapset.beatmaps[0].id}?bat_error=This beatmap has not enough nominations.'
        )

    update_beatmap_icon(
        beatmapset,
        DatabaseStatus.Qualified.value,
        beatmapset.status,
        session=session
    )

    beatmapsets.update(
        beatmapset.id,
        {
            'status': DatabaseStatus.Qualified.value,
            'approved_at': datetime.now(),
            'approved_by': current_user.id
        },
        session=session
    )

    beatmaps.update_by_set_id(
        beatmapset.id,
        {'status': DatabaseStatus.Qualified.value},
        session=session
    )

    move_beatmap_topic(
        beatmapset,
        DatabaseStatus.Qualified.value,
        session=session
    )

    app.session.logger.info(
        f'"{beatmapset.full_name}" was set to "Qualified" status by {current_user.name}.'
    )

    return redirect(
        f'/s/{beatmapset.id}'
    )

def handle_loved_status(beatmapset: DBBeatmapset, session: Session):
    update_beatmap_icon(
        beatmapset,
        DatabaseStatus.Loved.value,
        beatmapset.status,
        session=session
    )

    beatmapsets.update(
        beatmapset.id,
        {
            'status': DatabaseStatus.Loved.value,
            'approved_at': datetime.now(),
            'approved_by': current_user.id
        },
        session=session
    )

    beatmaps.update_by_set_id(
        beatmapset.id,
        {'status': DatabaseStatus.Loved.value},
        session=session
    )

    move_beatmap_topic(
        beatmapset,
        DatabaseStatus.Loved.value,
        session=session
    )

    app.session.logger.info(
        f'"{beatmapset.full_name}" was set to "Loved" status by {current_user.name}.'
    )

    return redirect(
        f'/s/{beatmapset.id}'
    )

@router.get('/status/<set_id>/update')
@login_required
def status_update(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    if (status := request.args.get('status', type=int)) == None:
        return abort(code=400)

    if status not in DatabaseStatus.values():
        return abort(code=400)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        status_handlers = {
            0: handle_pending_status,
            2: handle_approved_status,
            3: handle_qualified_status,
            4: handle_loved_status
        }

        if not (handler := status_handlers.get(status)):
            return abort(code=400)

        return handler(beatmapset, session)
