
from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.database.repositories import users
from app.models import UserModel

router = Blueprint("profile", __name__)

@router.get('/<user_id>')
@validate()
def profile(user_id: int) -> dict:
    if not (user := users.fetch_by_id(user_id)):
        return Response(
            response={},
            status=404,
            mimetype='application/json'
        )

    user.stats.sort(key=lambda x: x.mode)

    return UserModel.model_validate(user, from_attributes=True) \
                    .model_dump(exclude=['user'])
