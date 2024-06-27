
from app.common.database import beatmapsets, topics, posts, users, beatmaps
from app.common.constants import DatabaseStatus
from app.models import BeatmapsetModel

from flask_login import current_user, login_required
from flask import Blueprint, Response, request
from flask_pydantic import validate
from datetime import datetime

import app

router = Blueprint('profile-beatmaps', __name__)

@router.get('/<user_id>/beatmaps')
@validate()
def get_beatmaps(user_id: int):
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        user_beatmaps = beatmapsets.fetch_by_creator(
            user.id,
            session=session
        )

        return [
            BeatmapsetModel.model_validate(beatmapset, from_attributes=True) \
                           .model_dump()
            for beatmapset in user_beatmaps
        ]

@router.get('/<user_id>/beatmaps/revive')
@login_required
@validate()
def revive_beatmap(user_id: int):
    if current_user.id != user_id:
        return {
            'error': 403,
            'details': 'You are not authorized to perform this action.'
        }, 403

    if not (set_id := request.args.get('set_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "set_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return {
                'error': 404,
                'details': 'The requested beatmapset does not exist.'
            }, 404

        if beatmapset.creator_id != user.id:
            return {
                'error': 403,
                'details': 'You are not authorized to perform this action.'
            }, 403

        if beatmapset.status != DatabaseStatus.Graveyard:
            return {
                'error': 400,
                'details': 'The requested beatmapset is not in the graveyard.'
            }, 400

        beatmapsets.update(
            beatmapset.id,
            {
                'status': DatabaseStatus.WIP.value,
                'last_update': datetime.now()
            },
            session=session
        )

        beatmaps.update_by_set_id(
            beatmapset.id,
            {
                'status': DatabaseStatus.WIP.value,
                'last_update': datetime.now()
            },
            session=session
        )

        topics.update(
            beatmapset.topic_id,
            {
                'forum_id': 10,
                'icon_id': None
            },
            session=session
        )

        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 10},
            session=session
        )

        return BeatmapsetModel.model_validate(beatmapset, from_attributes=True) \
                              .model_dump()

@router.get('/<user_id>/beatmaps/delete')
@login_required
@validate()
def delete_beatmap(user_id: int):
    if current_user.id != user_id:
        return {
            'error': 403,
            'details': 'You are not authorized to perform this action.'
        }, 403

    if not (set_id := request.args.get('set_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "set_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return {
                'error': 404,
                'details': 'The requested beatmapset does not exist.'
            }, 404

        if beatmapset.creator_id != user.id:
            return {
                'error': 403,
                'details': 'You are not authorized to perform this action.'
            }, 403

        if beatmapset.status > 0:
            return {
                'error': 400,
                'details': 'The requested beatmapset cannot be deleted.'
            }, 400

        # Beatmap will be deleted on next bss upload
        beatmapsets.update(
            beatmapset.id,
            {'status': DatabaseStatus.Inactive.value},
            session=session
        )

        beatmaps.update_by_set_id(
            beatmapset.id,
            {'status': DatabaseStatus.Inactive.value},
            session=session
        )

        return {'success': True}
