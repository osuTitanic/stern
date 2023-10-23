
from flask import Blueprint, request, abort
from datetime import datetime, timedelta
from flask_pydantic import validate
from typing import List

from app.models import RankHistoryModel, PlaysHistoryModel, ReplayHistoryModel
from app.common.database.repositories import histories
from app.common.constants import GameMode

router = Blueprint("history", __name__)

@router.get('/<user_id>/history/rank/<mode>')
@validate()
def rank_history(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    if date_string := request.args.get('until'):
        until = datetime.fromisoformat(date_string)
    else:
        until = datetime.now() - timedelta(days=90)

    rank_history = histories.fetch_rank_history(
        user_id,
        mode.value,
        until
    )

    return [
        RankHistoryModel.model_validate(item, from_attributes=True) \
                        .model_dump()
        for item in rank_history
    ]

@router.get('/<user_id>/history/plays/<mode>')
@validate()
def plays_history(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    if date_string := request.args.get('until'):
        until = datetime.fromisoformat(date_string)
    else:
        until = datetime.now() - timedelta(days=90)

    plays_history = histories.fetch_plays_history(
        user_id,
        mode.value,
        until
    )

    return [
        PlaysHistoryModel.model_validate(item, from_attributes=True) \
                         .model_dump()
        for item in plays_history
    ]

@router.get('/<user_id>/history/views/<mode>')
@validate()
def replay_views_history(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    if date_string := request.args.get('until'):
        until = datetime.fromisoformat(date_string)
    else:
        until = datetime.now() - timedelta(days=90)

    replay_history = histories.fetch_replay_history(
        user_id,
        mode.value,
        until
    )

    return [
        ReplayHistoryModel.model_validate(item, from_attributes=True) \
                          .model_dump()
        for item in replay_history
    ]
