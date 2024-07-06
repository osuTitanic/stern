
from app.models.forums import PostModel, TopicModel
from app.common.database import posts, topics

from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint("topics-api", __name__)

@router.get('/topics/<topic_id>')
@validate()
def get_topic(topic_id: int):
    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested topic could not be found.'
            }, 404

        return TopicModel.model_validate(topic, from_attributes=True) \
                         .model_dump()

@router.get('/topics/<topic_id>/posts')
@validate()
def get_posts(topic_id: int):
    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested topic could not be found.'
            }, 404

        start = request.args.get(
            'start',
            default=0,
            type=int
        )

        topic_posts = posts.fetch_range_by_topic(
            topic.id,
            range=25,
            offset=start,
            session=session
        )

        return [
            PostModel.model_validate(post, from_attributes=True) \
                      .model_dump()
            for post in topic_posts
        ]
