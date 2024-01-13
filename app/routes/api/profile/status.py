
from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.cache import status, leaderboards

router = Blueprint("status", __name__)

@router.get('/<user_id>/status')
@validate()
def get_status(user_id: int) -> dict:
    if not (user_status := status.get(int(user_id))):
        return Response(
            response=(),
            status=404,
            mimetype='application/json'
        )

    return {
        'action': user_status.action.value,
        'mode': user_status.mode.value,
        'mods': user_status.mods.value,
        'beatmap_id': user_status.beatmap_id,
        'beatmap_checksum': user_status.beatmap_checksum,
        'beatmap_text': user_status.text,
        'version': status.version(user_id),
        'rankings': {
            'global': leaderboards.global_rank(user_id, user_status.mode.value),
            'ppv1': leaderboards.ppv1_rank(user_id, user_status.mode.value),
            'score': leaderboards.score_rank(user_id, user_status.mode.value),
            'total_score': leaderboards.total_score_rank(user_id, user_status.mode.value)
        }
    }
