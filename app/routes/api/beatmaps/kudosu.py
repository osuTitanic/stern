
from __future__ import annotations
from typing import Tuple

from app.common.database import beatmapsets, posts, modding
from app.common.database import DBForumPost, DBBeatmapset
from app.common.constants import DatabaseStatus
from app.models.kudosu import KudosuModel

from flask_login import current_user, login_required
from datetime import datetime, timedelta
from flask_pydantic import validate
from sqlalchemy.orm import Session
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
                'details': 'This beatmapset is already ranked.'
            }, 400

        if not (post := posts.fetch_one(post_id, session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.user_id == current_user.id:
            return {
                'error': 400,
                'details': 'You cannot modify kudosu on your own post.'
            }, 400

        existing_mod = modding.fetch_by_post_and_sender(
            post_id,
            current_user.id,
            session=session
        )

        topic_activity = (
            datetime.now() - post.topic.last_post_at
        )

        kudosu_amount = (
            1 if topic_activity < timedelta(days=7)
            else 2
        )

        if existing_mod:
            modding.update(
                existing_mod.id,
                {'amount': kudosu_amount},
                session=session
            )

            return KudosuModel.model_validate(existing_mod, from_attributes=True) \
                              .model_dump()

        kudosu = modding.create(
            target_id=post.user_id,
            sender_id=current_user.id,
            set_id=set_id,
            post_id=post_id,
            amount=kudosu_amount,
            session=session
        )

        return KudosuModel.model_validate(kudosu, from_attributes=True) \
                          .model_dump()

@router.get(f'/<set_id>/kudosu/<post_id>/revoke')
@login_required
@validate()
def revoke_kudosu(set_id: int, post_id: int):
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
                'details': 'This beatmapset is already ranked.'
            }, 400

        if not (post := posts.fetch_one(post_id, session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.user_id == current_user.id:
            return {
                'error': 400,
                'details': 'You cannot modify kudosu on your own post.'
            }, 400

        existing_mod = modding.fetch_by_post_and_sender(
            post_id,
            current_user.id,
            session=session
        )

        if existing_mod:
            modding.update(
                existing_mod.id,
                {'amount': -1},
                session=session
            )

            return KudosuModel.model_validate(existing_mod, from_attributes=True) \
                              .model_dump()

        kudosu = modding.create(
            target_id=post.user_id,
            sender_id=current_user.id,
            set_id=set_id,
            post_id=post_id,
            amount=-1,
            session=session
        )

        return KudosuModel.model_validate(kudosu, from_attributes=True) \
                          .model_dump()

@router.get(f'/<set_id>/kudosu/<post_id>/reset')
@login_required
@validate()
def reset_kudosu(set_id: int, post_id: int):
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
                'details': 'This beatmapset is already ranked.'
            }, 400

        if not (post := posts.fetch_one(post_id, session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.user_id == current_user.id:
            return {
                'error': 400,
                'details': 'You cannot modify kudosu on your own post.'
            }, 400

        existing_mod = modding.fetch_by_post_and_sender(
            post.id,
            current_user.id,
            session=session
        )

        if not existing_mod:
            return {
                'error': 404,
                'details': 'You have not given any kudosu to this post.'
            }, 404

        modding.delete(
            existing_mod.id,
            session=session
        )

        return {'success': True}
