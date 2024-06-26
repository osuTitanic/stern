
from app.models.forums import BookmarkModel
from app.common.database import users

from flask_login import current_user, login_required
from flask import Blueprint, Response
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
