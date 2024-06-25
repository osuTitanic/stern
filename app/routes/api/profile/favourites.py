
from app.common.database import favourites, beatmapsets
from app.models import BeatmapsetModel

from flask_login import current_user, login_required
from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint('beatmap-favourites', __name__)

@router.get('/<user_id>/favourites/')
@login_required
@validate()
def get_favourites(user_id: int):
    with app.session.database.managed_session() as session:
        user_favourites = favourites.fetch_many(
            user_id,
            session=session
        )

        return [
            {
                'set_id': fav.set_id,
                'user_id': fav.user_id,
                'created_at': str(fav.created_at),
                'beatmapset': (
                    BeatmapsetModel.model_validate(fav.beatmapset, from_attributes=True)
                                   .model_dump()
                )
            }
            for fav in user_favourites
        ]

@router.get('/<user_id>/favourites/add')
@login_required
@validate()
def add_favourite(user_id: int):
    if current_user.id != user_id:
        return {
            'error': 'unauthorized',
            'details': 'You are not authorized to perform this action.'
        }, 403

    if not (set_id := request.args.get('set_id', type=int)):
        return {
            'error': 'invalid_request',
            'details': 'The request is missing the required "set_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        beatmapset = beatmapsets.fetch_one(
            set_id,
            session=session
        )

        if not beatmapset:
            return {
                'error': 'not_found',
                'details': 'The requested beatmap was not found.'
            }, 404

        already_exists = favourites.fetch_one(
            current_user.id,
            beatmapset.id,
            session=session
        )

        if already_exists:
            return {
                'error': 'exists',
                'details': 'You have already added this beatmap to your favourites.'
            }, 400

        favourite = favourites.create(
            current_user.id,
            beatmapset.id,
            session=session
        )

        if not favourite:
            return {
                'error': 'failed',
                'details': (
                    'Something went wrong while trying to add this beatmap to your favourites.'
                    'Please try again!'
                )
            }, 500

        user_favourites = favourites.fetch_many(
            current_user.id,
            session=session
        )

        return [
            {
                'set_id': fav.set_id,
                'user_id': fav.user_id,
                'created_at': str(fav.created_at),
                'beatmapset': (
                    BeatmapsetModel.model_validate(fav.beatmapset, from_attributes=True)
                                   .model_dump()
                )
            }
            for fav in user_favourites
        ]

@router.get('/<user_id>/favourites/delete')
@login_required
@validate()
def delete_favourite(user_id: int):
    if current_user.id != user_id:
        return {
            'error': 'unauthorized',
            'details': 'You are not authorized to perform this action.'
        }, 403

    if not (set_id := request.args.get('set_id', type=int)):
        return {
            'error': 'invalid_request',
            'details': 'The request is missing the required "set_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        beatmapset = beatmapsets.fetch_one(
            set_id,
            session=session
        )

        if not beatmapset:
            return {
                'error': 'not_found',
                'details': 'The requested beatmap was not found.'
            }, 404

        is_deleted = favourites.delete(
            current_user.id,
            beatmapset.id,
            session=session
        )

        if not is_deleted:
            return {
                'error': 'no_favourite',
                'details': 'You have not added this beatmap to your favourites.'
            }, 400

        user_favourites = favourites.fetch_many(
            current_user.id,
            session=session
        )

        return [
            {
                'set_id': fav.set_id,
                'user_id': fav.user_id,
                'created_at': str(fav.created_at),
                'beatmapset': (
                    BeatmapsetModel.model_validate(fav.beatmapset, from_attributes=True)
                                   .model_dump()
                )
            }
            for fav in user_favourites
        ]
