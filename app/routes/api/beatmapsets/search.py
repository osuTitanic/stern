"""

    Sort By
    Offset
    Limit
    Mode
    Explicit Content
    Genre
    Language
    Has Video, Has Storyboard
    Played, Unplayed

"""

from flask import Blueprint, Response, request, jsonify
from pydantic import ValidationError
from flask_pydantic import validate

from app.common.database.repositories import beatmapsets
from app.models import SearchRequest, BeatmapsetModel

router = Blueprint('search', __name__)

@router.get('/search')
@validate()
def search_api():
    try:
        query = SearchRequest.model_validate(request.args.to_dict())
    except ValidationError as e:
        return Response(
            response=e.json(),
            status=400,
            mimetype='application/json'
        )

    results = beatmapsets.search_extended(
        query.query,
        query.genre,
        query.language,
        query.played,
        None, # TODO: user_id
        query.mode,
        query.status,
        query.sort,
        query.has_storyboard,
        query.has_video,
        query.offset,
        query.limit
    )

    return [
        BeatmapsetModel.model_validate(beatmapset, from_attributes=True) \
                       .model_dump()
        for beatmapset in results
    ]
