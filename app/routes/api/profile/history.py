
from flask import Blueprint, Response, request
from datetime import datetime, timedelta
from typing import List

from app.models import RankHistoryModel, PlaysHistoryModel, ReplayHistoryModel
from app.common.database.repositories import histories, users
from app.common.constants import GameMode

import app

router = Blueprint("history", __name__)

@router.get('/<user_id>/history/rank/<mode>')
def rank_history(
    user_id: str,
    mode: str
) -> List[dict]:
    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return Response(
                    response=(),
                    status=404,
                    mimetype='application/json'
                )

            user_id = user.id

        if (mode := GameMode.from_alias(mode)) is None:
            return Response(
                response={},
                status=400,
                mimetype='application/json'
            )

        if date_string := request.args.get('until'):
            until = datetime.fromisoformat(date_string)
        else:
            until = datetime.now() - timedelta(days=90)

        rank_history = histories.fetch_rank_history(
            user_id,
            mode.value,
            until,
            session=session
        )

        return [
            RankHistoryModel.model_validate(item, from_attributes=True) \
                            .model_dump()
            for item in rank_history
        ]

@router.get('/<user_id>/history/plays/<mode>')
def plays_history(
    user_id: str,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return Response(
            response={},
            status=400,
            mimetype='application/json'
        )

    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return Response(
                    response=(),
                    status=404,
                    mimetype='application/json'
                )

        else:
            if not (user := users.fetch_by_id(user_id, session=session)):
                return Response(
                    response=(),
                    status=404,
                    mimetype='application/json'
                )

        if date_string := request.args.get('until'):
            until = datetime.fromisoformat(date_string)
        else:
            until = user.created_at

        plays_history = histories.fetch_plays_history(
            user.id,
            mode.value,
            until,
            session=session
        )

        return [
            PlaysHistoryModel.model_validate(item, from_attributes=True) \
                             .model_dump()
            for item in plays_history
        ]

@router.get('/<user_id>/history/views/<mode>')
def replay_views_history(
    user_id: str,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return Response(
            response={},
            status=400,
            mimetype='application/json'
        )

    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return Response(
                    response=(),
                    status=404,
                    mimetype='application/json'
                )

        else:
            if not (user := users.fetch_by_id(user_id, session=session)):
                return Response(
                    response=(),
                    status=404,
                    mimetype='application/json'
                )

        if date_string := request.args.get('until'):
            until = datetime.fromisoformat(date_string)
        else:
            until = user.created_at

        replay_history = histories.fetch_replay_history(
            user.id,
            mode.value,
            until,
            session=session
        )

        return [
            ReplayHistoryModel.model_validate(item, from_attributes=True) \
                              .model_dump()
            for item in replay_history
        ]
