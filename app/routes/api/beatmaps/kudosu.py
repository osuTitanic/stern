
from __future__ import annotations
from app.common.database import beatmapsets, posts, modding
from app.common.constants import DatabaseStatus
from app.models.kudosu import KudosuModel

from flask_login import current_user, login_required
from flask_pydantic import validate
from datetime import timedelta
from flask import Blueprint

import app

router = Blueprint('beatmap-kudosu', __name__)

@router.get(f'/<set_id>/kudosu')
@validate()
def get_kudosu_by_set(set_id: int):
    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return {
                'error': 404,
                'details': 'The requested beatmapset could not be found.'
            }, 404

        kudosu = modding.fetch_all_by_set(
            set_id=beatmapset.id,
            session=session
        )

        return [
            KudosuModel.model_validate(k, from_attributes=True) \
                       .model_dump()
            for k in kudosu
        ]

@router.get(f'/<set_id>/kudosu/<post_id>')
@validate()
def get_kudosu_by_post(set_id: int, post_id: int):
    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if not beatmapsets.fetch_one(set_id, session):
            return {
                'error': 404,
                'details': 'The requested beatmapset could not be found.'
            }, 404

        kudosu = modding.fetch_all_by_post(
            post_id=post.id,
            session=session
        )

        return [
            KudosuModel.model_validate(k, from_attributes=True) \
                       .model_dump()
            for k in kudosu
        ]

@router.post(f'/<set_id>/kudosu/<post_id>/reward')
@login_required
@validate()
def reward_kudosu(set_id: int, post_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.post(f'/<set_id>/kudosu/<post_id>/revoke')
@login_required
@validate()
def revoke_kudosu(set_id: int, post_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.post(f'/<set_id>/kudosu/<post_id>/reset')
@login_required
@validate()
def reset_kudosu(set_id: int, post_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
