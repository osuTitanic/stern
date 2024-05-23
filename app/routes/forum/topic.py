
from app.common.database import forums, topics, posts
from flask import Blueprint, abort, request

import utils
import app

router = Blueprint("forum-topics", __name__)

@router.get('/<forum_id>/t/<id>')
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
