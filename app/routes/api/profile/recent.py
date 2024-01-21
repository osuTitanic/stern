
from flask import Blueprint, Response, request
from datetime import datetime, timedelta
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

import app

router = Blueprint("recent", __name__)

@router.get('/<user_id>/recent/<mode>')
@validate()
def recent_scores(
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

        try:
            if date_string := request.args.get('until'):
                until = datetime.fromisoformat(date_string)
            else:
                until = datetime.now() - timedelta(hours=24)

            min_status = max(0, int(request.args.get("min_status", 3)))
        except ValueError:
            return Response(
                response={},
                status=400,
                mimetype='application/json'
            )

        # Limit time
        until = sorted((
            datetime.now() - timedelta(days=30),
            until,
            datetime.now()
        ))[1]

        recent_plays = scores.fetch_recent_until(
            int(user_id),
            mode,
            until,
            min_status=min_status,
            session=session
        )

        return [
            ScoreModel.model_validate(score, from_attributes=True) \
                      .model_dump(exclude=['user'])
            for score in recent_plays
        ]
