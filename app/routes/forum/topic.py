
from app.common.database import DBForumTopic, DBForum
from app.common.helpers import ip
from app.common.database import (
    beatmapsets,
    forums,
    topics,
    posts
)

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required
from sqlalchemy.orm import Session

import utils
import app

router = Blueprint("forum-topics", __name__)

def update_views(topic_id: int, session: Session) -> None:
    ip_address = ip.resolve_ip_address_flask(request)

    lock = app.session.redis.get(f'forums:viewlock:{topic_id}:{ip_address}')

    if lock:
        return

    topics.update(
        topic_id,
        {'views': DBForumTopic.views + 1},
        session=session
    )

    app.session.redis.set(
        f'forums:viewlock:{topic_id}:{ip_address}',
        value=1,
        ex=60
    )

@router.get('/<forum_id>/t/<id>/')
def topic(forum_id: str, id: str):
    if not forum_id.isdigit():
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )

    if not id.isdigit():
        return abort(
            code=404,
            description=app.constants.TOPIC_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(id, session=session)):
            return abort(
                code=404,
                description=app.constants.TOPIC_NOT_FOUND
            )

        if topic.hidden:
            return abort(
                code=404,
                description=app.constants.TOPIC_NOT_FOUND
            )

        if topic.forum_id != int(forum_id):
            return redirect(
                f"/forum/{topic.forum_id}/t/{id}/"
            )

        page = max(1, request.args.get('page', 1, type=int))

        topic_posts = posts.fetch_range_by_topic(
            topic.id,
            range=12,
            offset=(page - 1) * 12,
            session=session
        )

        post_count = posts.fetch_count(
            topic_id=id,
            session=session
        )

        update_views(
            topic.id,
            session=session
        )

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

        initial_post = posts.fetch_initial_post(
            topic.id,
            session=session
        )

        if initial_post in topic_posts:
            # Override icon for initial post
            topic_posts[0].icon = topic.icon

        return utils.render_template(
            "forum/topic.html",
            css='forums.css',
            forum=topic.forum,
            topic=topic,
            posts=topic_posts,
            current_page=(page - 1),
            total_pages=post_count // 12,
            post_count=post_count,
            beatmapset=beatmapset,
            is_bookmarked=is_bookmarked,
            is_subscribed=is_subscribed,
            initial_post=initial_post,
            session=session
        )

@router.get('/<forum_id>/create')
@login_required
def create_post_view(forum_id: str):
    if not forum_id.isdigit():
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )
    
    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
            )
        
        return utils.render_template(
            "forum/create.html",
            css='forums.css',
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
    is_priviliged = (
        current_user.is_bat or
        current_user.is_moderator
    )

    if not forum.allow_icons and not is_priviliged:
        return

    icon_id = request.form.get(
        'icon',
        default=-1,
        type=int
    )

    if icon_id != -1:
        return icon_id

def get_type_dict() -> dict:
    if not current_user.is_moderator:
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
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )
    
    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session=session)):
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
            )

        if forum.hidden:
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

        title = request.form.get('title')
        content = request.form.get('bbcode')

        topic = topics.create(
            forum.id,
            current_user.id,
            title,
            session=session,
            can_change_icon=forum.allow_icons,
            icon_id=get_icon_id(forum),
            **get_type_dict()
        )

        posts.create(
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

        app.session.logger.info(
            f'{current_user.name} created a new topic "{topic.title}" ({topic.id}).'
        )

        return redirect(
            f"/forum/{forum.id}/t/{topic.id}"
        )
