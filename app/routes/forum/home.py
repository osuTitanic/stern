
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

        all_sub_forums = list(itertools.chain(*forum_dict.values()))
        sub_forum_ids = [forum.id for forum in all_sub_forums]

        forum_last_posts = posts.fetch_last_for_forums(
            sub_forum_ids,
            session=session
        )

        return utils.render_template(
            "forum/home.html",
            css='forums.css',
            title="Forums - Titanic",
            site_title="Titanic » Forums » Home",
            site_description="Discuss and share your thoughts with the community.",
            site_image=f"{app.config.OSU_BASEURL}/images/logo/main-low.png",
            forums=forum_dict,
            session=session,
            forum_recent={
                forum.id: forum_last_posts.get(forum.id)
                for forum in all_sub_forums
            }
        )
