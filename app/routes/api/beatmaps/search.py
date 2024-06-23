
from app.common.database.repositories import beatmapsets
from app.models import SearchRequest, BeatmapsetModel

from flask import Blueprint, Response, request
from flask_login import current_user
from pydantic import ValidationError
from flask_pydantic import validate

import app

router = Blueprint('search', __name__)

@router.get('/search')
@validate()
def search_api():
    with app.session.database.managed_session() as session:
        user_id = (
            current_user.id
            if not current_user.is_anonymous else None
        )

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
            user_id,
            query.mode,
            query.order,
            query.category,
            query.sort,
            query.storyboard,
            query.video,
            offset=query.page * 50,
            limit=50,
            session=session
        )

        return [
            BeatmapsetModel.model_validate(beatmapset, from_attributes=True) \
                           .model_dump()
            for beatmapset in results
        ]
