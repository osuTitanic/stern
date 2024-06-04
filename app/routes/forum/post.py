
from flask_login import login_required, current_user
from sqlalchemy.orm import Session
from flask import (
    Blueprint,
    Response,
    redirect,
    request,
    abort
)

from app.common.database import DBForumPost, DBForumTopic
from app.common.database import topics, posts

import utils
import app

router = Blueprint("forum-posts", __name__)

@router.get('/<forum_id>/t/<topic_id>/post/')
@login_required
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

        text = fetch_post_text(
            topic.id,
            action,
            int(action_id or '-1'),
            session=session
        )

        return utils.render_template(
            "forum/post.html",
            css='forums.css',
            current_text=text,
            forum=topic.forum,
            topic=topic,
            action=action,
            action_id=action_id
        )

def fetch_post_text(
    topic_id: int,
    action: str,
    action_id: int,
    session: Session
) -> str | None:
    if action == 'edit':
        if not action_id:
            return

        if not (post := posts.fetch_one(action_id, session=session)):
            return

        return post.content

    elif action == 'quote':
        if not action_id:
            return

        if not (post := posts.fetch_one(int(action_id), session=session)):
            return

        return f"[quote={post.user.name}]{post.content}[/quote]"

    elif action == 'post':
        drafts = posts.fetch_drafts(
            current_user.id,
            topic_id,
            session=session
        )

        if not drafts:
            return

        posts.delete(
            drafts[0].id,
            session=session
        )

        return drafts[0].content

def handle_post(topic: DBForumTopic, _: int, session: Session) -> Response:
    return abort(501) # TODO

def handle_topic_create(topic: DBForumTopic, _: int, session: Session) -> Response:
    return abort(501) # TODO

def handle_post_edit(topic: DBForumTopic, post_id: int, session: Session) -> Response:
    return abort(501) # TODO

@router.post('/<forum_id>/t/<topic_id>/post')
@login_required
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
            'edit': handle_post_edit,
            'quote': handle_post,
            'post': handle_post
        }

        if action not in actions:
            return abort(code=404)

        return actions[action](
            topic,
            action_id,
            session=session
        )
