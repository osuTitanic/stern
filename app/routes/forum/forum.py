
from app.common.database import forums, topics

from flask import Blueprint, abort, redirect, request

import utils
import math
import app

router = Blueprint("forum", __name__)

@router.get('/<forum_id>')
def forum_view(forum_id: int):
    if not forum_id.isdigit():
        return abort(
            code=404,
            description=app.constants.FORUM_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (forum := forums.fetch_by_id(forum_id, session)):
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
            )

        if forum.hidden:
            return abort(
                code=404,
                description=app.constants.FORUM_NOT_FOUND
            )

        if not forum.parent_id:
            # Forum can be viewed on front-page
            return redirect('/forum')

        page = max(request.args.get('page', 1, type=int), 1)
        topics_per_page = 25

        sub_forums = forums.fetch_sub_forums(forum.id, session)
        topic_count = forums.fetch_topic_count(forum_id, session)

        recent_topics = topics.fetch_recent_many(
            forum.id,
            limit=topics_per_page,
            offset=(page - 1) * topics_per_page,
            session=session
        )

        pinned_topics = topics.fetch_pinned_by_forum_id(
            forum.id,
            session=session
        )

        announcements = topics.fetch_announcements_by_forum_id(
            forum.id,
            limit=3,
            session=session
        )

        # Merge pinned topics with recent topics and
        # sort by id in descending order
        recent_topics = sorted(
            set(pinned_topics + recent_topics),
            key=lambda topic: math.inf if topic.pinned else topic.id,
            reverse=True
        )

        has_custom_icons = any(
            topic.icon_id
            for topic in recent_topics
        )

        return utils.render_template(
            "forum/forum.html",
            css='forums.css',
            title=f"{forum.name} - Titanic",
            site_title=f"Titanic » Forums » {forum.name}",
            site_description=forum.description,
            forum=forum,
            sub_forums=sub_forums,
            subforum_stats={
                subforum.id: (
                    forums.fetch_topic_count(subforum.id, session),
                    forums.fetch_post_count(subforum.id, session)
                )
                for subforum in sub_forums
            },
            subforum_recent={
                forum.id: topics.fetch_recent(forum.id, session)
                for forum in sub_forums
            },
            has_custom_icons=has_custom_icons,
            announcements=announcements,
            recent_topics=recent_topics,
            topic_count=topic_count,
            total_pages=topic_count // topics_per_page,
            current_page=page - 1,
            session=session
        )
