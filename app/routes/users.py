
from app.common.database.repositories import (
    infringements,
    activities,
    groups,
    users,
    stats
)

from flask import Blueprint, abort, redirect, request
from app.common.cache import status, leaderboards

import utils
import app

router = Blueprint('users', __name__)

@router.get('/<query>')
def userpage(query: str):
    if not query.isdigit():
        user = users.fetch_by_name_extended(query)

        if not user:
            abort(404)

        return redirect(f'/u/{user.id}')

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
            pp_rank=leaderboards.global_rank(user.id, int(mode)),
            pp_rank_country=leaderboards.country_rank(user.id, int(mode), user.country),
            score_rank=leaderboards.score_rank(user.id, int(mode)),
            score_rank_country=leaderboards.score_rank_country(user.id, int(mode), user.country),
            ppv1_rank=leaderboards.ppv1_rank(user.id, int(mode)),
            groups=groups.fetch_user_groups(user.id, session=session),
            infringements=infs
        )
