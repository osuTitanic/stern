
from app.common.database import forums, topics, posts

from flask import Blueprint, abort, redirect, request
from flask_login import current_user, login_required
from sqlalchemy.orm import Session

import utils
import app

router = Blueprint("forum-topics", __name__)

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

        if topic.forum_id != int(forum_id):
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
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

        return utils.render_template(
            "forum/topic.html",
            css='forums.css',
            forum=topic.forum,
            topic=topic,
            posts=topic_posts,
            current_page=(page - 1),
            total_pages=post_count // 12,
            post_count=post_count,
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
            forum=forum
        )

def update_notifications(notify: bool, user_id: int, topic_id: int, session: Session):
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

        type = request.form.get('type') # TODO
        title = request.form.get('title')
        content = request.form.get('bbcode')

        topic = topics.create(
            forum.id,
            current_user.id,
            title,
            session=session
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

        return redirect(
            f"/forum/{forum.id}/t/{topic.id}"
        )
