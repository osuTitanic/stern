
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
from app.common.database import DBForumPost, DBForumTopic, DBBeatmapset
from app.common.constants import NotificationType, DatabaseStatus
from app.common.database import (
    notifications,
    beatmapsets,
    beatmaps,
    topics,
    forums,
    posts
)

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
            return redirect(
                f"/forum/{topic.forum_id}/t/{topic.id}/post/"
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
            initial_post=initial_post,
            icons=forums.fetch_icons(session)
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

    type = request.form.get('type', default='global')

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

def update_beatmap_status(
    beatmapset: DBBeatmapset,
    status: DatabaseStatus,
    session: Session
) -> None:
    beatmapsets.update(
        beatmapset.id,
        {
            'status': status.value,
            'last_update': datetime.now()
        },
        session=session
    )
    beatmaps.update_by_set_id(
        beatmapset.id,
        {
            'status': status.value,
            'last_update': datetime.now()
        },
        session=session
    )

    if status > DatabaseStatus.Pending:
        beatmapsets.update(
            beatmapset.id,
            {
                'approved_at': datetime.now(),
                'approved_by': current_user.id
            },
            session=session
        )

def update_topic_location(
    topic: DBForumTopic,
    forum_id: int,
    session: Session
) -> None:
    topics.update(
        topic.id,
        {'forum_id': forum_id},
        session=session
    )
    posts.update_by_topic(
        topic.id,
        {'forum_id': forum_id},
        session=session
    )

def handle_beatmap_icon_update(
    icon_id: int | None,
    previous_icon: int | None,
    topic: DBForumTopic,
    session: Session
) -> None:
    if not current_user.is_bat:
        topics.update(
            topic.id,
            {'icon_id': previous_icon},
            session=session
        )
        return

    beatmapset = beatmapsets.fetch_by_topic(
        topic.id,
        session=session
    )

    if not beatmapset:
        return

    disallowed_statuses = (
        DatabaseStatus.Ranked,
        DatabaseStatus.Approved,
        DatabaseStatus.Loved
    )

    if beatmapset.status in disallowed_statuses:
        # Beatmap was already ranked
        # -> Set icon back to previous icon
        topics.update(
            topic.id,
            {'icon_id': previous_icon},
            session=session
        )
        return

    if icon_id == 1:
        # BAT wants to rank beatmapset
        if previous_icon != 3:
            # Beatmap was not bubbled
            topics.update(
                topic.id,
                {'icon_id': previous_icon},
                session=session
            )
            return

        # Qualify beatmapset
        # (Beatmap will automatically be ranked after 7 days)
        update_beatmap_status(
            beatmapset,
            DatabaseStatus.Qualified,
            session=session
        )

        # Move topic into ranked beatmaps forum
        update_topic_location(
            topic,
            forum_id=8,
            session=session
        )
        return

    if icon_id == 5:
        # TODO: Should this be "Loved" status?
        update_beatmap_status(
            beatmapset,
            DatabaseStatus.Approved,
            session=session
        )

        # Move topic into ranked beatmaps forum
        update_topic_location(
            topic,
            forum_id=8,
            session=session
        )
        return

    # All other statuses
    update_beatmap_status(
        beatmapset,
        DatabaseStatus.Pending,
        session=session
    )

    if topic.forum_id not in (9, 10):
        # Move topic back to pending beatmaps forum
        update_topic_location(
            topic,
            forum_id=9,
            session=session
        )

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

def notify_subscribers(post: DBForumPost, topic: DBForumTopic, session: Session):
    subscribers = topics.fetch_subscribers(
        topic.id,
        session=session
    )

    for subscriber in subscribers:
        if subscriber.user_id == current_user.id:
            continue

        notifications.create(
            subscriber.user_id,
            NotificationType.News.value,
            f'New Post',
            f'{current_user.name} posted something in "{topic.title}". Click here to view it!',
            link=f'/forum/{topic.forum_id}/p/{post.id}',
            session=session
        )

        # TODO: Send email, based on preferences

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
        post,
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

    is_priviliged = (
        current_user.is_bat or
        current_user.is_moderator
    )

    if post.edit_locked and not is_priviliged:
        return abort(
            403,
            description=app.constants.POST_LOCKED
        )

    user_id = request.form.get(
        'user_id',
        type=int,
        default=-1
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
        previous_icon = topic.icon_id

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
            previous_icon,
            topic,
            session=session
        )

    updates = {
        'content': content
    }

    if post.user_id == current_user.id:
        updates['edit_count'] = DBForumPost.edit_count + 1,
        updates['edit_time'] = datetime.now()

    posts.update(
        post.id,
        updates,
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
