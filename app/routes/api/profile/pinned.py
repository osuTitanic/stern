
from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

from flask_login import login_required, current_user
from flask import Blueprint, Response, request
from flask_pydantic import validate

import app

router = Blueprint("pinned", __name__)

@router.get('/<user_id>/pinned/add/<score_id>')
@login_required
@validate()
def add_pinned(user_id: int, score_id: int):
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        if user.id != current_user.id:
            return {
                'error': 403,
                'details': 'You are not authorized to perform this action.'
            }, 403

        if (score := scores.fetch_by_id(score_id, session)) is None:
            return {
                'error': 404,
                'details': 'The requested score could not be found.'
            }, 404

        if score.user_id != user.id:
            return {
                'error': 400,
                'details': 'The requested score was not set by the user.'
            }, 400

        if score.pinned:
            return {
                'error': 400,
                'details': 'The requested score is already pinned.'
            }, 400

        scores.update(
            score.id,
            {'pinned': True},
            session=session
        )

        return {'success': True}

@router.get('/<user_id>/pinned/remove/<score_id>')
@login_required
@validate()
def remove_pinned(user_id: int, score_id: int):
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        if user.id != current_user.id:
            return {
                'error': 403,
                'details': 'You are not authorized to perform this action.'
            }, 403

        if (score := scores.fetch_by_id(score_id, session)) is None:
            return {
                'error': 404,
                'details': 'The requested score could not be found.'
            }, 404

        if score.user_id != user.id:
            return {
                'error': 400,
                'details': 'The requested score was not set by the user.'
            }, 400

        if not score.pinned:
            return {
                'error': 400,
                'details': 'The requested score was not pinned.'
            }, 400

        scores.update(
            score.id,
            {'pinned': False},
            session=session
        )

        return {'success': True}

@router.get('/<user_id>/pinned/<mode_alias>')
@validate()
def get_pinned(
    user_id: int,
    mode_alias: str
):
    limit = request.args.get('limit', 10, int)
    offset = request.args.get('offset', 0, int)

    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        if (mode := GameMode.from_alias(mode_alias)) is None:
            return {
                'error': 400,
                'details': 'The requested mode does not exist.'
            }, 400

        limit = max(1, min(50, limit))

        pinned = scores.fetch_pinned(
            user.id,
            mode.value,
            limit,
            offset,
            session=session
        )

        pinned_count = scores.fetch_pinned_count(
            user.id,
            mode.value,
            session=session
        )

        return {
            'count': pinned_count,
            'scores': [
                ScoreModel.model_validate(score, from_attributes=True) \
                        .model_dump(exclude=['user'])
                for score in pinned
            ]
        }
