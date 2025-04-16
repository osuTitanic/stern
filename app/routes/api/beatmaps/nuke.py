
from flask_login import login_required
from flask import Blueprint, abort

router = Blueprint('beatmap-nuking', __name__)

@router.get('/<set_id>/nuke')
@login_required
def nuke_beatmap(set_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
