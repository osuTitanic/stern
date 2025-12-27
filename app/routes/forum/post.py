
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
from app.common.database import DBUser, DBForumPost, DBForumTopic, DBBeatmapset
from app.common.constants import NotificationType, BeatmapStatus, UserActivity
from app.common.helpers import activity
from app.common.database import (
    notifications,
    beatmapsets,
    nominations,
    topics,
    forums,
    posts
)

import hashlib
import utils
import app

router = Blueprint("forum-posts", __name__)

def broadcast_post_activity(
    topic: DBForumTopic,
    post: DBForumPost,
    author: DBUser,
    session: Session
) -> None:
    # Post to webhook & #announce channel
    activity.submit(
        author.id, None,
        UserActivity.ForumPostCreated,
        {
            'username': author.name,
            'post_id': post.id,
            'topic_name': topic.title,
            'topic_id': topic.id,
            'topic_icon': topic.icon.location if topic.icon else None,
            'content': post.content[:512] + ('...' if len(post.content) > 1024 else ''),
        },
        is_announcement=True,
        is_hidden=True,
        session=session
    )

@router.get('/<forum_id>/t/<topic_id>/post/')
@login_required
def post_view(forum_id: str, topic_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    if not topic_id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return utils.render_error(404, 'topic_not_found')

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

        beatmapset = beatmapsets.fetch_by_topic(
            topic.id,
            session=session
        )

        return utils.render_template(
            "forum/post.html",
            css='forums.css',
            title="Create a Post - Titanic",
            site_title=f"Titanic » Forums » {topic.forum.name} » {topic.title} » Post",
            site_description="Discuss and share your thoughts with the community.",
            current_text=text,
            forum=topic.forum,
            session=session,
            topic=topic,
            action=action,
            action_id=action_id,
            beatmapset=beatmapset,
            is_subscribed=is_subscribed,
            initial_post=initial_post,
            icons=forums.fetch_icons(session),
            topic_type=get_post_type(topic),
            topic_icon=topic.icon_id
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

        if post.deleted:
            return

        return post.content

    elif action == 'quote':
        if not action_id:
            return

        if not (post := posts.fetch_one(int(action_id), session=session)):
            return

        if post.deleted:
            return

        if post.content.strip('\r\n').startswith('[quote'):
            # Remove the quoted content from the post
            post.content = post.content.split('[/quote]', 1)[-1].strip('\r\n')

        return (
            f"[quote={post.user.name.replace('[', '').replace(']', '')}]"
            f"{post.content}"
            f"[/quote]"
        )

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

def get_post_type(topic: DBForumTopic) -> str:
    if topic.announcement:
        return 'announcement'

    if topic.pinned:
        return 'pinned'

    return 'global'

def update_topic_type(
    post: DBForumPost,
    topic: DBForumTopic,
    session: Session
) -> dict:
    if not current_user.is_moderator:
        return {}

    initial_post = posts.fetch_initial_post(
        topic.id,
        session=session
    )

    if post.id != initial_post.id:
        return {}

    type = request.form.get(
        key='type',
        default=get_post_type(topic)
    )

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

def get_icon_id(topic: DBForumTopic) -> int | None:
    is_privileged = (
        current_user.is_bat or
        current_user.is_moderator
    )
    
    if not is_privileged:
        return -2

    if not topic.can_change_icon:
        return -2

    icon_id = request.form.get(
        'icon',
        default=-1,
        type=int
    )

    if topic.icon_id == icon_id:
        return -2

    if icon_id != -1:
        return icon_id

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

def update_topic_status_text(
    beatmapset: DBBeatmapset,
    status: int,
    session: Session
) -> None:
    if not beatmapset.topic_id:
        return

    if beatmapset.status > BeatmapStatus.Pending:
        topics.update(
            beatmapset.topic_id,
            {'status_text': None},
            session=session
        )

    elif status == BeatmapStatus.Graveyard:
        topics.update(
            beatmapset.topic_id,
            {'status_text': None},
            session=session
        )

    else:
        beatmap_nominations = nominations.count(
            beatmapset.id,
            session=session
        )

        if beatmap_nominations > 0:
            topics.update(
                beatmapset.topic_id,
                {'status_text': 'Waiting for approval...'},
                session=session
            )
            return

        last_bat_post = posts.fetch_last_bat_post(
            beatmapset.topic_id,
            session=session
        )

        if not last_bat_post:
            topics.update(
                beatmapset.topic_id,
                {'status_text': 'Needs modding'},
                session=session
            )
            return

        last_creator_post = posts.fetch_last_by_user(
            beatmapset.topic_id,
            beatmapset.creator_id,
            session=session
        )

        if not last_creator_post:
            topics.update(
                beatmapset.topic_id,
                {'status_text': 'Waiting for creator\'s response...'},
                session=session
            )
            return

        if last_bat_post.id > last_creator_post.id:
            topics.update(
               beatmapset.topic_id,
                {'status_text': "Waiting for creator's response..."},
                session=session
            )
            return

        topics.update(
            beatmapset.topic_id,
            {'status_text': 'Waiting for further modding...'},
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
            NotificationType.Forum.value,
            f'New Post',
            f'{current_user.name} posted something in "{topic.title}". Click here to view it!',
            link=f'/forum/{topic.forum_id}/p/{post.id}',
            session=session
        )

        # TODO: Send email, based on preferences

def handle_post(topic: DBForumTopic, _: int, session: Session) -> Response:
    if topic.locked_at and not current_user.is_moderator:
        return utils.render_error(403, 'topic_locked')

    content = request.form.get(
        'bbcode',
        type=str
    )

    last_post = posts.fetch_last_by_user(
        topic.id,
        current_user.id,
        session=session
    )

    # Prevent users from spamming posts too quickly
    last_post_delta = (
        (datetime.now() - last_post.created_at).total_seconds()
        if last_post else float('inf')
    )

    if last_post_delta <= 2:
        # We'll assume that this is part of the "duplicate post" bug
        # and redirect them to their last post instead of showing an error
        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}/p/{last_post.id}"
        )

    if last_post_delta < 8:
        return utils.render_error(429, 'posting_too_quickly')

    if not content:
        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}"
        )

    new_icon = get_icon_id(topic)

    post = posts.create(
        topic.id,
        topic.forum_id,
        current_user.id,
        content,
        icon_id=(
            new_icon
            if new_icon != -2
            else None
        ),
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

    topic_updates = {
        'last_post_at': datetime.now(),
        'icon_id': (
            new_icon
            if new_icon != -2
            else topic.icon_id
        )
    }

    if current_user.is_moderator:
        locked = request.form.get(
            'locked',
            type=bool,
            default=False
        )

        topic_updates['locked_at'] = (
            datetime.now()
            if locked
            else None
        )

    if current_user.is_admin:
        topic_status = request.form.get(
            'topic-status',
            type=str,
            default=''
        ) or None

        if topic_status != topic.status_text:
            topic_updates['status_text'] = topic_status

    topics.update(
        topic.id,
        topic_updates,
        session=session
    )

    beatmapset = beatmapsets.fetch_by_topic(
        topic.id,
        session=session
    )

    if beatmapset and not topic_updates.get('status_text'):
        update_topic_status_text(
            beatmapset,
            beatmapset.status,
            session=session
        )

    broadcast_post_activity(
        topic, post,
        current_user,
        session=session
    )

    app.session.logger.info(
        f'{current_user.name} created a post on "{topic.title}" ({post.id}).'
    )

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/p/{post.id}"
    )

def handle_post_edit(topic: DBForumTopic, post_id: int, session: Session) -> Response:
    if topic.locked_at and not current_user.is_moderator:
        return utils.render_error(403, 'topic_locked')

    if not (post := posts.fetch_one(post_id, session=session)):
        return utils.render_error(404, 'post_not_found')

    is_priviliged = (
        current_user.is_bat or
        current_user.is_moderator
    )

    if post.edit_locked and not is_priviliged:
        return utils.render_error(403, 'post_locked')

    if current_user.id != post.user_id and not is_priviliged:
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

    topic_type = update_topic_type(
        post,
        topic,
        session=session
    )

    if topic_type:
        topics.update(
            topic.id,
            topic_type,
            session=session
        )

    updates = {
        'content': content
    }

    if is_priviliged:
        updates['edit_locked'] = request.form.get(
            'edit-locked',
            type=bool,
            default=False
        )

    if post.user_id == current_user.id:
        updates['edit_count'] = post.edit_count + 1,
        updates['edit_time'] = datetime.now()

    posts.update(
        post.id,
        updates,
        session=session
    )

    app.session.logger.info(
        f'{current_user.name} edited their post ({post.id}).'
    )

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/p/{post.id}"
    )

def handle_draft_save(topic: DBForumTopic, _: int, session: Session) -> Response:
    content = request.form.get(
        'bbcode',
        type=str
    )

    if not content:
        return redirect(f"/forum/{topic.forum_id}/t/{topic.id}")

    drafts = posts.fetch_drafts(
        current_user.id,
        topic.id,
        session=session
    )

    # Delete old draft(s)
    for draft in drafts:
        posts.delete(draft.id, session=session)

    draft = posts.create(
        topic.id,
        topic.forum_id,
        current_user.id,
        content,
        draft=True,
        hidden=True,
        session=session
    )

    app.session.logger.info(f'{current_user.name} saved a draft ({draft.id}).')
    return redirect(f"/forum/{topic.forum_id}/t/{topic.id}/")

@router.post('/<forum_id>/t/<topic_id>/post')
@login_required
def do_post(forum_id: str, topic_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    if not topic_id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return utils.render_error(404, 'topic_not_found')

        if topic.forum_id != int(forum_id):
            return utils.render_error(404, 'forum_not_found')

        if current_user.silence_end:
            return utils.render_error(403, 'user_silenced')

        if current_user.restricted:
            return utils.render_error(403, 'user_restricted')

        action = request.form.get('action', default='post')
        action_id = request.form.get('id', type=int)

        content = request.form.get(
            'bbcode',
            type=str
        )

        if len(content) > 2**14 and not current_user.is_moderator:
            return utils.render_error(400, 'post_too_long')

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

@router.post('/<forum_id>/t/<topic_id>/draft')
@login_required
def do_draft_save(forum_id: str, topic_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    if not topic_id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session=session)):
            return utils.render_error(404, 'topic_not_found')

        if topic.forum_id != int(forum_id):
            return utils.render_error(404, 'forum_not_found')

        if current_user.silence_end:
            return utils.render_error(403, 'user_silenced')

        if current_user.restricted:
            return utils.render_error(403, 'user_restricted')

        action_id = request.form.get('id', type=int)
        content = request.form.get('bbcode', type=str)

        if len(content) > 2**14 and not current_user.is_moderator:
            return utils.render_error(400, 'post_too_long')

        return handle_draft_save(
            topic,
            action_id,
            session=session
        )
