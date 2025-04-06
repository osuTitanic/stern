
from app.common.database import forums, posts
from flask import Blueprint

import app.session
import itertools
import utils

router = Blueprint("forum-home", __name__)

@router.route("/")
def home():
    with app.session.database.managed_session() as session:
        main_forums = forums.fetch_main_forums(session)

        forum_dict = {
            forum: forums.fetch_sub_forums(forum.id, session)
            for forum in main_forums
        }

        return utils.render_template(
            "forum/home.html",
            css='forums.css',
            title="Forums - Titanic",
            site_title="Titanic » Forums » Home",
            site_description="Discuss and share your thoughts with the community.",
            forums=forum_dict,
            session=session,
            forum_stats={
                forum.id: (
                    forums.fetch_topic_count(forum.id, session),
                    forums.fetch_post_count(forum.id, session)
                )
                for forum in itertools.chain(*forum_dict.values())
            },
            forum_recent={
                forum.id: posts.fetch_last_by_forum(forum.id, session)
                for forum in itertools.chain(*forum_dict.values())
            }
        )
