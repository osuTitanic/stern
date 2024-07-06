
from app.models.forums import ForumModel, TopicModel
from app.common.database import forums, topics

from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint("forums-api", __name__)

@router.get('/<forum_id>')
@validate()
def get_forum(forum_id: int):
    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested forum could not be found.'
            }, 404

        return ForumModel.model_validate(forum, from_attributes=True) \
                        .model_dump()

@router.get('/<forum_id>/topics')
@validate()
def get_topics(forum_id: int):
    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested forum could not be found.'
            }, 404

        start = request.args.get(
            'start',
            default=0,
            type=int
        )

        forum_topics = topics.fetch_recent_many(
            forum.id,
            limit=50,
            offset=start,
            session=session
        )

        return [
            TopicModel.model_validate(topic, from_attributes=True) \
                      .model_dump()
            for topic in forum_topics
        ]
