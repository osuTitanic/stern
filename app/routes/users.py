
from app.common.database.repositories import (
    infringements,
    activities,
    groups,
    names,
    users,
    stats
)

from flask import Blueprint, abort, redirect, request
from app.common.cache import status, leaderboards
from app.common.constants import GameMode

import config
import utils
import app

router = Blueprint('users', __name__)

@router.get('/<query>')
def userpage(query: str):
    query = query.strip()

    if not query.isdigit():
        # Searching for username based on user query
        if user := users.fetch_by_name_extended(query):
            return redirect(f'/u/{user.id}')

        # Search name history as a backup
        if name := names.fetch_by_name_extended(query):
            return redirect(f'/u/{name.user_id}')

        return abort(404)

    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_id(int(query), session)):
            return abort(404)

        if not user.activated:
            return abort(404)

        if not (mode := request.args.get('mode')):
            mode = user.preferred_mode

        if user.restricted:
            infs = infringements.fetch_all(
                user.id,
                session=session
            )

        else:
            infs = infringements.fetch_recent_until(
                user.id,
                session=session
            )

        pp_rank = leaderboards.global_rank(user.id, int(mode))
        pp_rank_country = leaderboards.country_rank(user.id, int(mode), user.country)
        score_rank = leaderboards.score_rank(user.id, int(mode))
        score_rank_country = leaderboards.score_rank_country(user.id, int(mode), user.country)
        ppv1_rank = leaderboards.ppv1_rank(user.id, int(mode))

        return utils.render_template(
            name='user.html',
            user=user,
            css='user.css',
            mode=int(mode),
            title=f"{user.name} - Titanic",
            is_online=status.exists(user.id),
            achievement_categories=app.constants.ACHIEVEMENTS,
            achievements={a.name:a for a in user.achievements},
            activity=activities.fetch_recent(user.id, int(mode), session=session),
            current_stats=stats.fetch_by_mode(user.id, int(mode), session=session),
            groups=groups.fetch_user_groups(user.id, session=session),
            site_title=f"{user.name} - Player Info",
            site_description=f"Rank ({GameMode(mode).formatted}): Global: #{pp_rank} | Country: #{pp_rank_country}",
            site_image=f"https//osu.{config.DOMAIN_NAME}/a/{user.id}",
            site_url=f"https://osu.{config.DOMAIN_NAME}/u/{user.id}",
            pp_rank=pp_rank,
            pp_rank_country=pp_rank_country,
            score_rank=score_rank,
            score_rank_country=score_rank_country,
            ppv1_rank=ppv1_rank,
            infringements=infs
        )
