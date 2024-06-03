
from sqlalchemy.orm import Session
from flask import (
    Blueprint,
    Response,
    redirect,
    request,
    abort
)

from app.common.database import DBForumPost, DBForumTopic
from app.common.database import topics

import utils
import app

router = Blueprint("forum-posts", __name__)

@router.get('/<forum_id>/t/<topic_id>/post')
def post_view(forum_id: str, topic_id: str):
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

        allowed_actions = (
            'create',
            'post',
            'edit',
            'quote'
        )

        if action not in allowed_actions:
            return abort(code=404)

        return utils.render_template(
            "forum/post.html",
            css='forums.css',
            forum=topic.forum,
            topic=topic,
            action=action,
            action_id=action_id
        )

def handle_post(topic: DBForumTopic, _: int, session: Session) -> Response:
    return abort(501) # TODO

def handle_topic_create(topic: DBForumTopic, _: int, session: Session) -> Response:
    return abort(501) # TODO

def handle_post_edit(topic: DBForumTopic, post_id: int, session: Session) -> Response:
    return abort(501) # TODO

@router.post('/<forum_id>/t/<topic_id>/post')
def do_post(forum_id: str, topic_id: str):
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

        actions = {
            'create': handle_topic_create,
            'post': handle_post,
            'edit': handle_post_edit,
            'quote': handle_post
        }

        if action not in actions:
            return abort(code=404)

        return actions[action](
            topic,
            action_id,
            session=session
        )
