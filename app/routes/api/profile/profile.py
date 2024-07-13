
from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.database.repositories import users
from app.models import UserModel

import app

router = Blueprint("profile", __name__)

@router.get('/<user_id>')
@validate()
def profile(user_id: str) -> dict:
    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404

        else:
            if not (user := users.fetch_by_id(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404

        user.stats.sort(key=lambda x: x.mode)

        return UserModel.model_validate(user, from_attributes=True) \
                        .model_dump()
