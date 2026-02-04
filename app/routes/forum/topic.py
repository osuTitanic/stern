
from app.common.database import DBForumTopic, DBForumPost, DBForum, DBUser
from app.common.config import config_instance as config
from app.common.helpers import activity, permissions
from app.common.constants import UserActivity
from app.common.database import (
    beatmapsets,
    forums,
    topics,
    posts,
    users
)

from . import activity as forum_activity
from flask_login import current_user, login_required
from flask import Blueprint, redirect, request
from sqlalchemy.orm import Session

import utils
import app

router = Blueprint("forum-topics", __name__)

def broadcast_topic_activity(
    topic: DBForumTopic,
    post: DBForumPost,
    author: DBUser,
    session: Session
) -> None:
    # Post to webhook & #announce channel
    activity.submit(
        author.id, None,
        UserActivity.ForumTopicCreated,
        {
            'username': author.name,
            'topic_name': topic.title,
            'forum_name': topic.forum.name,
            'forum_id': topic.forum_id,
            'topic_id': topic.id,
            'topic_icon': topic.icon.location if topic.icon else None,
            'content': post.content[:512] + ('...' if len(post.content) > 1024 else ''),
        },
        is_announcement=True,
        session=session
    )

@router.get('/<forum_id>/t/<id>/')
def topic(forum_id: str, id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    if not id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(id, session=session)):
            return utils.render_error(404, 'topic_not_found')

        if topic.hidden:
            return utils.render_error(404, 'topic_not_found')

        if topic.forum_id != int(forum_id):
            return redirect(
                f"/forum/{topic.forum_id}/t/{id}/"
            )

        if current_user.is_authenticated:
            # Used for "Current users browsing this forum"
            forum_activity.mark_user_active(current_user.id, topic.forum_id)

        page = max(1, request.args.get('page', 1, type=int))

        topic_posts = posts.fetch_range_by_topic(
            topic.id,
            range=15,
            offset=(page - 1) * 15,
            session=session
        )

        post_count = posts.fetch_count(
            topic_id=id,
            session=session
        )

        forum_activity.update_topic_read_state(topic.id)
        forum_activity.update_views(topic.id, session=session)

        beatmapset = beatmapsets.fetch_by_topic(
            topic.id,
            session=session
        )

        is_subscribed = False
        is_bookmarked = False

        if current_user.is_authenticated:
            is_subscribed = topics.is_subscribed(
                topic.id,
                current_user.id,
                session=session
            )

            is_bookmarked = topics.is_bookmarked(
                topic.id,
                current_user.id,
                session=session
            )

            forum_activity.mark_user_active(
                current_user.id,
                topic.forum_id
            )

        initial_post = posts.fetch_initial_post(
            topic.id,
            session=session
        )

        if not initial_post:
            return utils.render_error(404, 'topic_not_found')

        if initial_post in topic_posts:
            # Override icon for initial post
            topic_posts[0].icon = topic.icon

        active_users = users.fetch_usernames(
            forum_activity.get_active_users(topic.forum_id),
            session=session
        )

        return utils.render_template(
            "forum/topic.html",
            css='forums.css',
            title=f"{topic.title} - Titanic",
            site_title=f"Titanic » Forums » {topic.forum.name} » {topic.title}",
            site_description=initial_post.content.split('\n')[0],
            site_image=f'{config.OSU_BASEURL}{app.filters.avatar_url(initial_post.user)}',
            canonical_url=request.base_url,
            forum=topic.forum,
            topic=topic,
            posts=topic_posts,
            current_page=page,
            post_count=post_count,
            beatmapset=beatmapset,
            active_users=active_users,
            is_bookmarked=is_bookmarked,
            is_subscribed=is_subscribed,
            initial_post=initial_post,
            session=session
        )

@router.get('/<forum_id>/create')
@login_required
def create_post_view(forum_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return utils.render_error(404, 'forum_not_found')

        if not permissions.has_permission("forum.topics.create", current_user.id):
            return utils.render_error(403)

        return utils.render_template(
            "forum/create.html",
            css='forums.css',
            title="Create a Topic - Titanic",
            site_title=f"Titanic » Forums » {forum.name} » Create",
            site_description="Discuss and share your thoughts with the community.",
            session=session,
            forum=forum,
            icons=forums.fetch_icons(session)
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

def get_icon_id(forum: DBForum) -> int | None:
    can_force_change_icon = permissions.has_permission(
        "forum.moderation.topics.edit_icon",
        current_user.id
    )
    can_change_icon = (
        permissions.has_permission("forum.topics.edit_icon", current_user.id) and
        forum.allow_icons
    )

    # BATs are able to change icons of topics that allow icon changes
    # Moderators can change icons regardless of forum settings
    can_change_icon = can_change_icon or can_force_change_icon

    if not can_change_icon:
        return

    icon_id = request.form.get(
        'icon',
        default=-1,
        type=int
    )

    if icon_id != -1:
        return icon_id

def get_topic_options() -> dict:
    can_set_options = permissions.has_permission(
        "forum.moderation.topics.set_options",
        current_user.id
    )

    if not can_set_options:
        return {}

    type = request.form.get('type')

    if type == 'announcement':
        return {'announcement': True}

    if type == 'pinned':
        return {'pinned': True}

    return {}

@router.post('/<forum_id>/create')
@login_required
def create_post_action(forum_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')
    
    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return utils.render_error(404, 'forum_not_found')

        if forum.hidden:
            return utils.render_error(404, 'forum_not_found')

        if not permissions.has_permission("forum.topics.create", current_user.id):
            return utils.render_error(403)

        if current_user.silence_end:
            return utils.render_error(403, 'user_silenced')

        if current_user.restricted:
            return utils.render_error(403, 'user_restricted')

        title = request.form.get('title')
        content = request.form.get('bbcode')

        if not title or not content:
            return redirect(f"/forum/{forum.id}")

        topic = topics.create(
            forum.id,
            current_user.id,
            title,
            session=session,
            can_change_icon=forum.allow_icons,
            icon_id=get_icon_id(forum),
            **get_topic_options()
        )

        post = posts.create(
            topic.id,
            forum.id,
            current_user.id,
            content,
            session=session
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

        broadcast_topic_activity(
            topic,
            post,
            current_user,
            session=session
        )

        app.session.logger.info(
            f'{current_user.name} created a new topic "{topic.title}" ({topic.id}).'
        )

        return redirect(
            f"/forum/{forum.id}/t/{topic.id}"
        )
