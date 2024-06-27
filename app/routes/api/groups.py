
from app.common.database.repositories import groups
from app.models.groups import GroupModel
from app.models.user import UserModel
from flask_pydantic import validate
from flask import Blueprint

import app

router = Blueprint("groups", __name__)

@router.get('/')
def get_all_groups():
    with app.session.database.managed_session() as session:
        public_groups = groups.fetch_all(session=session)
        public_groups.sort(key=lambda g: g.id)

        return [
            {
                'group': GroupModel.model_validate(group, from_attributes=True).model_dump(),
                'users': [
                    UserModel.model_validate(user, from_attributes=True).model_dump()
                    for user in groups.fetch_group_users(group.id, session=session)
                ]
            }
            for group in public_groups
        ]

@router.get('/<id>')
@validate()
def get_group(id: int):
    with app.session.database.managed_session() as session:
        group = groups.fetch_one(id, session=session)

        if not group:
            return {
                'error': 404,
                'details': 'The requested group could not be found.'
            }, 404

        if group.hidden:
            return {
                'error': 404,
                'details': 'The requested group could not be found.'
            }, 404

        return {
                'group': GroupModel.model_validate(group, from_attributes=True).model_dump(),
                'users': [
                    UserModel.model_validate(user, from_attributes=True).model_dump()
                    for user in groups.fetch_group_users(group.id, session=session)
                ]
            }
