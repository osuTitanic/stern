
from flask_login import login_required
from flask import Blueprint

router = Blueprint('beatmap-status', __name__)

@router.post('/status/difficulty')
@login_required
def diff_status_update():
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.get('/status/<set_id>/update')
@login_required
def status_update(set_id: int):
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
