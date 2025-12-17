
from app.common.database.repositories import (
    collaborations,
    relationships,
    infringements,
    activities,
    modding,
    groups,
    names,
    users,
    stats
)

from flask import Response, abort, Blueprint, redirect, request
from app.common.config import config_instance as config
from app.common.cache import status, leaderboards
from app.common.database.objects import DBUser
from app.common.constants import GameMode
from sqlalchemy.orm import Session

import utils
import app

router = Blueprint('users', __name__)
preload = (DBUser.relationships, DBUser.achievements)

@router.get('/users/<query>')
def modern_userpage_redirect(query: str) -> Response:
    return redirect(f'/u/{query}')

@router.get('/u/<query>')
def userpage(query: str):
    query = query.strip()

    with app.session.database.managed_session() as session:
        if not query.isdigit():
            # Searching for username based on user query
            return resolve_user_by_name(query, session=session)

        user_id = int(query)

        if not (user := users.fetch_by_id(user_id, *preload, session=session)):
            return utils.render_error(404, 'user_not_found')

        if not user.activated:
            return utils.render_error(404, 'user_not_found')

        mode = user.preferred_mode
        mode_query = request.args.get('mode')

        if mode_query and mode_query.isdigit():
            mode = int(mode_query)

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

        followers = relationships.fetch_count_by_target(
            user.id,
            session=session
        )
        
        rankings = leaderboards.player_rankings(
            user.id, mode, user.country,
            leaderboards=(
                "performance",
                "rscore",
                "tscore",
                "ppv1",
                "leader"
            )
        )

        pp_ranking = rankings.get("performance", None)
        pp_rank = pp_ranking["global"] if pp_ranking else None
        pp_rank_country = pp_ranking["country"] if pp_ranking else None

        score_ranking = rankings.get("rscore", None)
        score_rank = score_ranking["global"] if score_ranking else None
        score_rank_country = score_ranking["country"] if score_ranking else None

        tscore_ranking = rankings.get("tscore", None)
        total_score_rank = tscore_ranking["global"] if tscore_ranking else None

        firsts_ranking = rankings.get("leader", None)
        firsts_rank = firsts_ranking["global"] if firsts_ranking else None

        ppv1_ranking = rankings.get("ppv1", None)
        ppv1_rank = ppv1_ranking["global"] if ppv1_ranking else None

        return utils.render_template(
            template_name='user.html',
            user=user,
            mode=mode,
            css='user.css',
            title=f"{user.name} - Titanic",
            site_title=f"{user.name} - Player Info",
            site_description=f"Rank ({GameMode(int(mode)).formatted}): Global: #{pp_rank or '-'} | Country: #{pp_rank_country or '-'}",
            site_image=f'{config.OSU_BASEURL}{app.filters.avatar_url(user)}',
            site_url=f"{config.OSU_BASEURL}/u/{user.id}",
            canonical_url=f"/u/{user.id}",
            is_online=status.exists(user.id),
            achievement_categories=app.constants.ACHIEVEMENTS,
            achievements={a.name:a for a in user.achievements},
            collaborations=collaborations.fetch_beatmaps_by_user(user.id, session=session),
            total_kudosu=modding.total_amount_by_user(user.id, session=session),
            recent_mods=modding.fetch_range_by_user(user.id, session=session),
            activity=activities.fetch_recent(user.id, int(mode), session=session),
            current_stats=stats.fetch_by_mode(user.id, int(mode), session=session),
            total_posts=users.fetch_post_count(user.id, session=session),
            groups=groups.fetch_user_groups(user.id, session=session),
            total_score_rank=total_score_rank,
            score_rank_country=score_rank_country,
            score_rank=score_rank,
            pp_rank_country=pp_rank_country,
            pp_rank=pp_rank,
            ppv1_rank=ppv1_rank,
            firsts_rank=firsts_rank,
            followers=followers,
            infringements=infs,
            rankings=rankings,
            session=session
        )

def resolve_user_by_name(query: str, session: Session) -> Response:
    if user := users.fetch_by_name_extended(query, session):
        return redirect(f'/u/{user.id}')

    # Search name history as a backup
    if name := names.fetch_by_name_extended(query, session):
        return redirect(f'/u/{name.user_id}')

    return utils.render_error(404, 'user_not_found')
