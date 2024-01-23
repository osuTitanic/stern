
from __future__ import annotations

from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.database.repositories import scores
from app.models import ScoreModel

import app

router = Blueprint("scores", __name__)

@router.get("/<score_id>")
@validate()
def get_score(score_id: int) -> dict | Response:
    with app.session.database.managed_session() as session:
        score = scores.fetch_by_id(score_id, session=session)

        if not score:
            return Response(
                response={},
                status=404,
                mimetype="application/json"
            )

        return ScoreModel.model_validate(score, from_attributes=True) \
                         .model_dump()
