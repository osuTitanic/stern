
from app.common.database import users, topics
from app.models.forums import BookmarkModel

from flask_login import current_user, login_required
from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint("forum-bookmarks", __name__)

@router.get('/bookmarks')
@login_required
@validate()
def get_bookmarks():
    with app.session.database.managed_session() as session:
        bookmarks = users.fetch_bookmarks(
            current_user.id,
            session=session
        )

        bookmarks = [
            bookmark
            for bookmark in bookmarks
            if not bookmark.topic.hidden
        ]

        return [
            BookmarkModel.model_validate(bookmark, from_attributes=True) \
                         .model_dump()
            for bookmark in bookmarks
        ]

@router.get('/bookmarks/add')
@login_required
@validate()
def add_bookmark():
    if not (topic_id := request.args.get('topic_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "topic_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session)):
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        if topic.hidden:
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        topics.add_bookmark(
            topic_id,
            current_user.id,
            session=session
        )

        bookmarks = users.fetch_bookmarks(
            current_user.id,
            session=session
        )

        bookmarks = [
            bookmark
            for bookmark in bookmarks
            if not bookmark.topic.hidden
        ]

        return [
            BookmarkModel.model_validate(bookmark, from_attributes=True) \
                         .model_dump()
            for bookmark in bookmarks
        ]

@router.get('/bookmarks/remove')
@login_required
@validate()
def remove_bookmark():
    if not (topic_id := request.args.get('topic_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "topic_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session)):
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        if topic.hidden:
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        topics.delete_bookmark(
            topic_id,
            current_user.id,
            session=session
        )

        bookmarks = users.fetch_bookmarks(
            current_user.id,
            session=session
        )

        bookmarks = [
            bookmark
            for bookmark in bookmarks
            if not bookmark.topic.hidden
        ]

        return [
            BookmarkModel.model_validate(bookmark, from_attributes=True) \
                         .model_dump()
            for bookmark in bookmarks
        ]
