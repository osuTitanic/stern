
from app.common.database import beatmapsets, posts, modding
from app.common.constants import DatabaseStatus
from app.models.kudosu import KudosuModel

from flask_login import current_user, login_required
from flask import Blueprint, request
from flask_pydantic import validate

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

@router.get(f'/<set_id>/kudosu/<post_id>/reward')
@login_required
@validate()
def reward_kudosu(set_id: int, post_id: int):
    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return {
                'error': 404,
                'details': 'The requested beatmapset could not be found.'
            }, 404

        if not beatmapset.topic_id:
            return {
                'error': 400,
                'details': 'This beatmapset is not linked to a forum topic.'
            }, 400

        if current_user.id != beatmapset.creator_id and not current_user.is_bat:
            return {
                'error': 403,
                'details': 'You are not authorized to perform this action.'
            }, 403

        if beatmapset.status >= DatabaseStatus.Ranked:
            return {
                'error': 400,
                'details': 'This beatmapset is already ranked, no kudosu can be rewarded.'
            }, 400

        if not (post := posts.fetch_one(post_id, session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.user_id == current_user.id:
            return {
                'error': 400,
                'details': 'You cannot reward kudosu to your own post.'
            }, 400

        existing_mod = modding.fetch_by_post_and_sender(
            post_id,
            current_user.id,
            session=session
        )

        if existing_mod:
            return {
                'error': 400,
                'details': 'You have already rewarded kudosu to this post.'
            }, 400

        kudosu_amount = {
            DatabaseStatus.Pending: 1,
            DatabaseStatus.Graveyard: 2,
            DatabaseStatus.WIP: 2
        }

        kudosu = modding.create(
            target_id=post.user_id,
            sender_id=current_user.id,
            set_id=set_id,
            post_id=post_id,
            amount=kudosu_amount.get(beatmapset.status, 0),
            session=session
        )

        return KudosuModel.model_validate(kudosu, from_attributes=True) \
                          .model_dump()
