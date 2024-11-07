
from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.cache import status, leaderboards

router = Blueprint("status", __name__)

@router.get('/<user_id>/status')
@validate()
def get_status(user_id: int) -> dict:
    if not (stats := status.get(user_id)):
        return {
            'error': 404,
            'details': 'The requested user could not be found.'
        }, 404
    
    user_status = stats.status
    mode = user_status.mode.value

    return {
        'action': user_status.action.value,
        'mode': user_status.mode.value,
        'mods': user_status.mods.value,
        'beatmap_id': user_status.beatmap_id,
        'beatmap_checksum': user_status.beatmap_checksum,
        'beatmap_text': user_status.text,
        'version': status.version(user_id),
        'rankings': {
            'global': leaderboards.global_rank(user_id, mode),
            'ppv1': leaderboards.ppv1_rank(user_id, mode),
            'score': leaderboards.score_rank(user_id, mode),
            'total_score': leaderboards.total_score_rank(user_id, mode)
        },
        'stats': {
            'rscore': stats.rscore,
            'tscore': stats.tscore,
            'accuracy': stats.accuracy,
            'playcount': stats.playcount,
            'rank': stats.rank,
            'pp': stats.pp
        }
    }
