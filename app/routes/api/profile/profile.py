
from flask_pydantic import validate
from flask import Blueprint, abort
from typing import List

from app.common.database.repositories import users
from app.models import UserModel

router = Blueprint("profile", __name__)

@router.get('/<user_id>')
@validate()
def profile(user_id: int) -> List[dict]:
    if not (user := users.fetch_by_id(user_id)):
        return abort(404)

    return [
        UserModel.model_validate(user, from_attributes=True) \
                 .model_dump(exclude=['user'])
    ]
