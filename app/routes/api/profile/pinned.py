
from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

from flask_login import login_required, current_user
from flask import Blueprint, Response, request
from flask_pydantic import validate

import app

router = Blueprint("pinned", __name__)

@router.get('/<user_id>/pinned/<mode_alias>')
@validate()
def get_pinned(
    user_id: int,
    mode_alias: str
):
    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(user_id, session)):
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

        pinned = scores.fetch_pinned(user.id, mode.value, session)

        return [
            ScoreModel.model_validate(score, from_attributes=True) \
                      .model_dump(exclude=['user'])
            for score in pinned
        ]
