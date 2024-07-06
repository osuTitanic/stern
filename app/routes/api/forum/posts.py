
from app.models.forums import PostModel
from app.common.database import posts

from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint("posts-api", __name__)

@router.get('/posts/<post_id>')
@validate()
def get_post(post_id: int):
    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session=session)):
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.topic.hidden:
            return {
                'error': 404,
                'details': 'The requested post could not be found.'
            }, 404

        if post.deleted:
            post.content = '[ Deleted ]'

        return PostModel.model_validate(post, from_attributes=True) \
                        .model_dump()
