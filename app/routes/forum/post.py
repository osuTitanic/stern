
from flask_login import login_required, current_user
from sqlalchemy.orm import Session
from datetime import datetime
from flask import (
    Blueprint,
    Response,
    redirect,
    request,
    abort
)

from app.common.database import DBForumPost, DBForumTopic
from app.common.database import topics, posts, forums

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
            'post',
            'edit',
            'quote'
        )

        if action not in allowed_actions:
            return abort(code=404)

        is_subscribed = topics.is_subscribed(
            topic.id,
            current_user.id,
            session=session
        )

        text = fetch_post_text(
            topic.id,
            action,
            int(action_id or '-1'),
            session=session
        )

        initial_post = posts.fetch_initial_post(
            topic.id,
            session=session
        )

        return utils.render_template(
            "forum/post.html",
            css='forums.css',
            current_text=text,
            forum=topic.forum,
            topic=topic,
            action=action,
            action_id=action_id,
            is_subscribed=is_subscribed,
            initial_post=initial_post
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

def update_topic_type() -> dict:
    if not current_user.is_moderator:
        return {}

    type = request.form.get('type')

    if type == 'announcement':
        return {
            'announcement': True,
            'pinned': False
        }

    if type == 'pinned':
        return {
            'pinned': True,
            'announcement': False
        }

    return {
        'pinned': False,
        'announcement': False
    }

def update_icon_id(topic: DBForumTopic) -> dict:
    is_priviliged = (
        current_user.is_bat or
        current_user.is_moderator
    )

    if not topic.can_change_icon and not is_priviliged:
        return

    icon_id = request.form.get(
        'icon',
        default=-1,
        type=int
    )

    if icon_id != -1:
        return {'icon_id': icon_id}

    return {'icon_id': None}

def handle_beatmap_icon_update(
    icon_id: int | None,
    topic: DBForumTopic,
    session: Session
) -> None:
    ... # TODO

def update_notifications(
    notify: bool,
    user_id: int,
    topic_id: int,
    session: Session
) -> None:
    if notify:
        topics.add_subscriber(
            topic_id,
            user_id,
            session=session
        )
        return

    topics.delete_subscriber(
        topic_id,
        user_id,
        session=session
    )

def notify_subscribers(topic: DBForumTopic, session: Session):
    ... # TODO

def handle_post(topic: DBForumTopic, _: int, session: Session) -> Response:
    if topic.locked_at:
        return abort(
            403,
            description=app.constants.TOPIC_LOCKED
        )

    content = request.form.get(
        'bbcode',
        type=str
    )

    if not content:
        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}"
        )

    post = posts.create(
        topic.id,
        topic.forum_id,
        current_user.id,
        content,
        session=session
    )

    notify = request.form.get(
        'notify',
        type=bool,
        default=False
    )

    notify_subscribers(
        topic,
        session=session
    )

    update_notifications(
        notify,
        current_user.id,
        topic.id,
        session=session
    )

    topics.update(
        topic.id,
        {'last_post_at': datetime.now()},
        session=session
    )

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/p/{post.id}"
    )

def handle_post_edit(topic: DBForumTopic, post_id: int, session: Session) -> Response:
    if topic.locked_at:
        return abort(
            403,
            description=app.constants.TOPIC_LOCKED
        )

    if not (post := posts.fetch_one(post_id, session=session)):
        return abort(
            404,
            description=app.constants.POST_NOT_FOUND
        )

    if post.edit_locked:
        return abort(
            403,
            description=app.constants.POST_LOCKED
        )

    user_id = request.form.get(
        'user_id',
        type=int,
        default=-1
    )

    is_priviliged = (
        current_user.is_bat or
        current_user.is_moderator
    )

    if post.user_id != user_id and not is_priviliged:
        return abort(403)

    content = request.form.get(
        'bbcode',
        type=str
    )

    if not content:
        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}/p/{post.id}"
        )

    notify = request.form.get(
        'notify',
        type=bool,
        default=False
    )

    update_notifications(
        notify,
        current_user.id,
        topic.id,
        session=session
    )

    initial_post = posts.fetch_initial_post(
        topic.id,
        session=session
    )

    if post.id == initial_post.id:
        topic_updates = {
            **update_icon_id(topic),
            **update_topic_type()
        }

        topics.update(
            topic.id,
            topic_updates,
            session=session
        )

        handle_beatmap_icon_update(
            topic_updates.get('icon_id'),
            topic,
            session=session
        )

    posts.update(
        post.id,
        {
            'content': content,
            'edit_count': DBForumPost.edit_count + 1,
            'edit_time': datetime.now()
        },
        session=session
    )

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/p/{post.id}"
    )

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

        if current_user.silence_end:
            return abort(
                code=403,
                description=app.constants.USER_SILENCED
            )

        if current_user.restricted:
            return abort(
                code=403,
                description=app.constants.USER_RESTRICTED
            )

        action = request.form.get('action', default='post')
        action_id = request.form.get('id', type=int)

        actions = {
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
