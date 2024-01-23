
from flask import Blueprint, Response
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import achievements, users
from app.models import AchievementModel

import app

router = Blueprint("achievements", __name__)

@router.get('/<user_id>/achievements')
@validate()
def user_achievements(user_id: str) -> List[dict]:
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

        if not (user_achievements := achievements.fetch_many(int(user_id), session=session)):
            return Response(
                response={},
                status=404,
                mimetype='application/json'
            )

        return [
            AchievementModel.model_validate(achievement, from_attributes=True) \
                            .model_dump()
            for achievement in user_achievements
        ]
