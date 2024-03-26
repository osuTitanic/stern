
from app.common.database import forums, topics
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
            forums=forum_dict,
            forum_stats={
                forum.id: (
                    forums.fetch_topic_count(forum.id, session),
                    forums.fetch_post_count(forum.id, session)
                )
                for forum in itertools.chain(*forum_dict.values())
            },
            forum_recent={
                forum.id: topics.fetch_recent(forum.id, session)
                for forum in itertools.chain(*forum_dict.values())
            }
        )
