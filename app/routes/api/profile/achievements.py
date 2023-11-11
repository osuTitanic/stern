
from flask import Blueprint, Response
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import achievements
from app.models import AchievementModel

router = Blueprint("achievements", __name__)

@router.get('/<user_id>/achievements')
@validate()
def user_achievements(user_id: int) -> List[dict]:
    if not (user_achievements := achievements.fetch_many(user_id)):
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
