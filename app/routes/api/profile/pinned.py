
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
            return Response(
                response={},
                status=404,
                mimetype='application/json'
            )

        if user.id != current_user.id:
            return Response(
                response={},
                status=403,
                mimetype='application/json'
            )

        if (score := scores.fetch_by_id(score_id, session)) is None:
            return Response(
                response={},
                status=404,
                mimetype='application/json'
            )

        if score.user_id != user.id:
            return Response(
                response={},
                status=403,
                mimetype='application/json'
            )

        if score.pinned:
            return Response(
                response={},
                status=200,
                mimetype='application/json'
            )

        scores.update(
            score.id,
            {'pinned': True},
            session=session
        )

        return Response(
            response={},
            status=200,
            mimetype='application/json'
        )

@router.get('/<user_id>/pinned/remove/<score_id>')
@login_required
@validate()
def remove_pinned(user_id: int, score_id: int):
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session=session)):
            return Response(
                response={},
                status=404,
                mimetype='application/json'
            )

        if user.id != current_user.id:
            return Response(
                response={},
                status=403,
                mimetype='application/json'
            )

        if (score := scores.fetch_by_id(score_id, session)) is None:
            return Response(
                response={},
                status=404,
                mimetype='application/json'
            )

        if score.user_id != user.id:
            return Response(
                response={},
                status=403,
                mimetype='application/json'
            )

        if not score.pinned:
            return Response(
                response={},
                status=200,
                mimetype='application/json'
            )

        scores.update(
            score.id,
            {'pinned': False},
            session=session
        )

        return Response(
            response={},
            status=200,
            mimetype='application/json'
        )

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
            return Response(
                response=(),
                status=404,
                mimetype='application/json'
            )

        if (mode := GameMode.from_alias(mode_alias)) is None:
            return Response(
                response={},
                status=400,
                mimetype='application/json'
            )

        limit = max(1, min(50, limit))

        pinned = scores.fetch_pinned(
            user.id,
            mode.value,
            limit,
            offset,
            session=session
        )

        return [
            ScoreModel.model_validate(score, from_attributes=True) \
                      .model_dump(exclude=['user'])
            for score in pinned
        ]
