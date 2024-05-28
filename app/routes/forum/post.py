
from flask import Blueprint, abort, request

from app.common.database import topics

import utils
import app

router = Blueprint("forum-posts", __name__)

@router.get('/<forum_id>/t/<topic_id>/post')
def post(forum_id: str, topic_id: str):
    if not forum_id.isdigit():
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )

    if not topic_id.isdigit():
        return abort(
            code=404,
            description=app.constants.TOPIC_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return abort(
                code=404,
                description=app.constants.TOPIC_NOT_FOUND
            )

        if topic.forum_id != int(forum_id):
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
            )

        action = request.args.get('action', default='post')
        action_id = request.args.get('id', type=int)

        if action not in ('post', 'edit'):
            return abort(code=404)

        return utils.render_template(
            "forum/post.html",
            css='forums.css',
            forum=topic.forum,
            topic=topic,
            action=action,
            action_id=action_id
        )
