
from app.common.database import beatmaps
from app.models import BeatmapModel

from flask import Blueprint, Response
from flask_pydantic import validate

router = Blueprint('beatmap', __name__)

@router.get('/<id>')
@validate()
def get_beatmap(id: int):
    if not (beatmap := beatmaps.fetch_by_id(id)):
        return {
            'error': 404,
            'details': 'The requested beatmap could not be found.'
        }, 404

    if beatmap.status <= -3:
        return {
            'error': 404,
            'details': 'The requested beatmap could not be found.'
        }, 404

    return BeatmapModel.model_validate(beatmap, from_attributes=True) \
                       .model_dump()
