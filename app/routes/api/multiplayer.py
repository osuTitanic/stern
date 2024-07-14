
from app.common.database.repositories import matches, events
from app.models import MatchModel, MatchEventModel

from flask import Blueprint, request
from datetime import datetime

import app

router = Blueprint('multiplayer', __name__)

@router.get('/match/<id>')
def get_match(id: int):
    with app.session.database.managed_session() as session:
        if not (match := matches.fetch_by_id(id, session=session)):
            return {
                'error': 404,
                'details': 'The requested match could not be found.'
            }, 404

        return MatchModel.model_validate(match, from_attributes=True) \
                         .model_dump()

@router.get('/match/<id>/events')
def get_events(id: int):
    with app.session.database.managed_session() as session:
        if not (match := matches.fetch_by_id(id, session=session)):
            return {
                'error': 404,
                'details': 'The requested match could not be found.'
            }, 404

        start_time = match.created_at

        if after_timestamp := request.args.get('after', None, type=int):
            # Fetch events aftet the given timestamp
            start_time = datetime.utcfromtimestamp(after_timestamp / 1000)

        match_events = events.fetch_all_after_time(
            match.id,
            start_time,
            session=session
        )

        return [
            MatchEventModel.model_validate(event, from_attributes=True) \
                           .model_dump()
            for event in match_events
        ]
