
from app.common.database import nominations
from app.models.user import UserModel
from flask_login import login_required
from flask import Blueprint

import config
import app

router = Blueprint('beatmap-nomination', __name__)

@router.get('/nominations/<set_id>')
def get_nominations(set_id: int):
    with app.session.database.managed_session() as session:
        nominations_list = nominations.fetch_by_beatmapset(
            set_id,
            session=session
        )

        return [
            {
                'set_id': nom.set_id,
                'user_id': nom.user_id,
                'created_at': str(nom.time),
                'user': (
                    UserModel.model_validate(nom.user, from_attributes=True) \
                             .model_dump()
                )
            }
            for nom in nominations_list
        ]

@router.get('/nominations/<set_id>/add')
@login_required
def add_nomination(set_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.get('/nominations/<set_id>/reset')
@login_required
def reset_nominations(set_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
