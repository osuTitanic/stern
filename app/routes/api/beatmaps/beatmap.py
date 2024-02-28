
from app.common.database import beatmaps
from app.models import BeatmapModel

from flask import Blueprint, Response
from flask_pydantic import validate

router = Blueprint('beatmap', __name__)

@router.get('/<id>')
@validate()
def get_beatmap(id: int):
    if not (beatmap := beatmaps.fetch_by_id(id)):
        return Response(
            response={},
            status=404,
            mimetype='application/json'
        )

    return BeatmapModel.model_validate(beatmap, from_attributes=True) \
                       .model_dump()
