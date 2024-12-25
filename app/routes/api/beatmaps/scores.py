
from app.models import ScoreModelWithoutBeatmap, ScoreModel, BeatmapModel
from app.common.database import beatmaps, scores
from app.common.constants import GameMode

from flask import Blueprint, request
from flask_pydantic import validate

import config
import app

router = Blueprint('beatmap-scores', __name__)

@router.get('/<id>/scores')
@validate()
def get_beatmap_scores(id: int):
    with app.session.database.managed_session() as session:
        if not (beatmap := beatmaps.fetch_by_id(id, session=session)):
            return {
                'error': 404,
                'details': 'The requested beatmap could not be found.'
            }, 404
        
        mode = request.args.get('mode')
        valid_modes = GameMode._member_map_.values()

        if mode and not mode.isdigit():
            return {
                'error': 400,
                'details': 'Invalid mode parameter.'
            }, 400
        
        if mode and int(mode) not in valid_modes:
            return {
                'error': 400,
                'details': 'Invalid mode.'
            }, 400

        top_scores = scores.fetch_range_scores(
            beatmap.id,
            mode=int(mode or beatmap.mode),
            limit=config.SCORE_RESPONSE_LIMIT,
            session=session
        )

        return {
            'beatmap': BeatmapModel.model_validate(beatmap, from_attributes=True).model_dump(),
            'scores': [
                ScoreModelWithoutBeatmap.model_validate(score, from_attributes=True).model_dump()
                for score in top_scores
            ]
        }

@router.get('/<id>/scores/users/<user_id>')
@validate()
def get_beatmap_user_score(id: int, user_id: int):
    with app.session.database.managed_session() as session:
        if not (beatmap := beatmaps.fetch_by_id(id, session=session)):
            return {
                'error': 404,
                'details': 'The requested beatmap could not be found.'
            }, 404

        mode = request.args.get('mode')
        valid_modes = GameMode._member_map_.values()

        if mode and not mode.isdigit():
            return {
                'error': 400,
                'details': 'Invalid mode parameter.'
            }, 400
        
        if mode and int(mode) not in valid_modes:
            return {
                'error': 400,
                'details': 'Invalid mode.'
            }, 400
        
        score = scores.fetch_personal_best(
            beatmap.id,
            user_id,
            mode=int(mode or beatmap.mode),
            session=session
        )

        if not score:
            return {
                'error': 404,
                'details': 'The user could not be found or has not set a score on this beatmap.'
            }, 404

        return ScoreModel.model_validate(score, from_attributes=True).model_dump()
