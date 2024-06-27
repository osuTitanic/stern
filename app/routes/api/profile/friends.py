
from app.common.database.repositories import users, relationships
from flask_login import current_user, login_required
from flask import Blueprint, Response, request

import json
import app

router = Blueprint("friends", __name__)

@router.get('/friends/add')
@login_required
def add_friend():
    if not (user_id := request.args.get('id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (target := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        current_friends = relationships.fetch_target_ids(
            current_user.id,
            session
        )

        if target.id not in current_friends:
            # Create relationship
            relationships.create(
                current_user.id,
                target.id,
                status=0,
                session=session
            )

        status = 'friends'

        # Check for mutual
        target_friends = relationships.fetch_target_ids(
            target.id,
            session
        )

        if current_user.id in target_friends:
            status = 'mutual'

        return {'status': status}

@router.get('/friends/remove')
@login_required
def remove_friend():
    if not (user_id := request.args.get('id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (target := users.fetch_by_id(user_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested user could not be found.'
            }, 404

        current_friends = relationships.fetch_target_ids(
            current_user.id,
            session=session
        )

        if target.id not in current_friends:
            return {
                'error': 400,
                'details': 'You are not friends with this user.'
            }, 400

        relationships.delete(
            current_user.id,
            target.id,
            status=0,
            session=session
        )

        status = 'friends'

        # Check for mutual
        target_friends = relationships.fetch_target_ids(
            target.id,
            session
        )

        if current_user.id in target_friends:
            status = 'mutual'

        return {'status': status}
