
from app.common.database.repositories import users, relationships
from flask import Blueprint, Response, request

import flask_login
import json
import app

router = Blueprint("friends", __name__)

@router.get('/friends/add')
@flask_login.login_required
def add_friend():
    if not (user_id := request.args.get('id', type=int)):
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    with app.session.database.managed_session() as session:
        if not (target := users.fetch_by_id(user_id, session)):
            return Response(
                response=(),
                status=404,
                mimetype='application/json'
            )

        current_friends = relationships.fetch_target_ids(
            flask_login.current_user.id,
            session
        )

        if target.id not in current_friends:
            # Create relationship
            relationships.create(
                flask_login.current_user.id,
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

        if flask_login.current_user.id in target_friends:
            status = 'mutual'

        return Response(
            response=json.dumps({'status': status}),
            status=200,
            mimetype='application/json'
        )

@router.get('/friends/remove')
@flask_login.login_required
def remove_friend():
    if not (user_id := request.args.get('id', type=int)):
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    with app.session.database.managed_session() as session:
        if not (target := users.fetch_by_id(user_id, session)):
            return Response(
                response=(),
                status=404,
                mimetype='application/json'
            )

        current_friends = relationships.fetch_target_ids(
            flask_login.current_user.id,
            session
        )

        if target.id not in current_friends:
            return Response(
                response=(),
                status=400,
                mimetype='application/json'
            )

        relationships.delete(
            flask_login.current_user.id,
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

        if flask_login.current_user.id in target_friends:
            status = 'mutual'

        return Response(
            response=json.dumps({'status': status}),
            status=200,
            mimetype='application/json'
        )
