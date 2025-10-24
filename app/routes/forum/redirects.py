
from flask import Blueprint, redirect, abort, request
from app.common.database import topics, posts

import utils
import app

router = Blueprint("forum-redirects", __name__)

@router.get('/<forum_id>/t/<topic_id>/p/<post_id>/')
def get_topic_by_post_and_topic(forum_id: str, topic_id: str, post_id: str):
    if not forum_id.isdigit():
        return utils.render_error(404, 'forum_not_found')

    if not topic_id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    if not post_id.isdigit():
        return utils.render_error(404, 'post_not_found')

    with app.session.database.managed_session() as session:
        post = posts.fetch_one(post_id, session=session)

        if not post:
            return utils.render_error(404, 'post_not_found')

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
        return utils.render_error(404, 'forum_not_found')

    if not post_id.isdigit():
        return utils.render_error(404, 'post_not_found')

    with app.session.database.managed_session() as session:
        post = posts.fetch_one(post_id, session=session)

        if not post:
            return utils.render_error(404, 'post_not_found')

        return redirect(
            f"/forum/{forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/t/<id>/')
def topic_redirect(id: str):
    if not id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(id, session=session)):
            return utils.render_error(404, 'topic_not_found')

        return redirect(
            f"/forum/{topic.forum_id}/t/{topic.id}/"
        )

@router.get('/t/<topic_id>/p/<post_id>/')
def topic_post_redirect(topic_id: str, post_id: str):
    if not topic_id.isdigit():
        return utils.render_error(404, 'topic_not_found')

    if not post_id.isdigit():
        return utils.render_error(404, 'post_not_found')

    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session=session)):
            return utils.render_error(404, 'post_not_found')

        return redirect(
            f"/forum/{post.topic.forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/p/<post_id>/')
def post_redirect(post_id: str):
    if not post_id.isdigit():
        return utils.render_error(404, 'post_not_found')

    with app.session.database.managed_session() as session:
        if not (post := posts.fetch_one(post_id, session=session)):
            return utils.render_error(404, 'post_not_found')

        return redirect(
            f"/forum/{post.topic.forum_id}/t/{post.topic_id}/p/{post.id}/"
        )

@router.get('/posting.php')
def quick_reply_redirect():
    topic_id = request.args.get('t', type=int)

    if not topic_id:
        return utils.render_error(404, 'topic_not_found')

    if not (topic := topics.fetch_one(topic_id)):
        return utils.render_error(404, 'topic_not_found')

    return redirect(
        f"/forum/{topic.forum_id}/t/{topic.id}/post"
    )

@router.get('/viewtopic.php')
def viewtopic_redirect():
    topic_id = request.args.get('t', type=int)
    post_id = request.args.get('p', type=int)

    if post_id:
        post = posts.fetch_one(post_id)

        if not post:
            return utils.render_error(404, 'post_not_found')
        
        return redirect(
            f"/forum/t/{post.topic_id}/p/{post.id}"
        )

    if topic_id:
        topic = topics.fetch_one(topic_id)

        if not topic:
            return utils.render_error(404, 'topic_not_found')

        return redirect(
            f"/forum/t/{topic.id}"
        )
    
    return utils.render_error(404, 'topic_not_found')

@router.get('/viewforum.php')
def viewforum_redirect():
    forum_id = request.args.get('f', type=int)

    if not forum_id:
        return utils.render_error(404, 'forum_not_found')

    return redirect(
        f"/forum/{forum_id}"
    )

@router.get('/ucp.php')
def user_control_panel():
    redirect_map = {
        'register': '/account/register',
        'sendpassword': '/account/reset',
        'avatar': '/account/profile#avatar',
    }

    return redirect(
        redirect_map.get(request.args.get('mode'), '/account')
    )

@router.get('/index.php')
def index_redirect():
    return redirect('/forum')
