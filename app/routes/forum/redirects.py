
from flask import Blueprint, redirect, abort, request
from app.common.database import topics, posts

import app

router = Blueprint("forum-redirects", __name__)

@router.get('/<forum_id>/t/<topic_id>/p/<post_id>/')
def get_topic_by_post_and_topic(forum_id: str, topic_id: str, post_id: str):
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

    if not post_id.isdigit():
        return abort(
            code=404,
            description=app.constants.POST_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        post = posts.fetch_one(post_id, session=session)

        if not post:
            return abort(
                code=404,
                description=app.constants.POST_NOT_FOUND
            )

        page_count = posts.fetch_count_before_post(
            post_id,
            topic_id,
            session=session
        )

        page = (page_count // 15) + 1

        return redirect(
            f"/forum/{forum_id}/t/{topic_id}/?page={page}#post-{post_id}"
        )

@router.get('/<forum_id>/p/<post_id>/')
def get_topic_by_post(forum_id: str, post_id: str):
    if not forum_id.isdigit():
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )

    if not post_id.isdigit():
        return abort(
            code=404,
            description=app.constants.POST_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        post = posts.fetch_one(post_id, session=session)

        if not post:
            return abort(
                code=404,
                description=app.constants.POST_NOT_FOUND
            )

        return redirect(
            f"/forum/{forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/t/<id>/')
def topic_redirect(id: str):
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

        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}/"
        )

@router.get('/t/<topic_id>/p/<post_id>/')
def topic_post_redirect(topic_id: str, post_id: str):
    if not topic_id.isdigit():
        return abort(
            code=404,
            description=app.constants.TOPIC_NOT_FOUND
        )

    if not post_id.isdigit():
        return abort(
            code=404,
            description=app.constants.POST_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session=session)):
            return abort(
                code=404,
                description=app.constants.POST_NOT_FOUND
            )

        return redirect(
            f"/forum/{post.topic.forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/p/<post_id>/')
def post_redirect(post_id: str):
    if not post_id.isdigit():
        return abort(
            code=404,
            description=app.constants.POST_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session=session)):
            return abort(
                code=404,
                description=app.constants.POST_NOT_FOUND
            )

        return redirect(
            f"/forum/{post.topic.forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/posting.php')
def quick_reply_redirect():
    topic_id = request.args.get('t', type=int)

    if not topic_id:
        return abort(
            code=404,
            description=app.constants.TOPIC_NOT_FOUND
        )

    if not (topic := topics.fetch_one(topic_id)):
        return abort(
            code=404,
            description=app.constants.TOPIC_NOT_FOUND
        )

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/post"
    )
