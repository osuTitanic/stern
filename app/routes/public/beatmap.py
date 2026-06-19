
from app.common.database.objects import DBScore, DBBeatmap
from app.common.database import beatmaps, scores, favourites, nominations, relationships, collaborations
from app.common.constants import BeatmapLanguage, BeatmapGenre, BeatmapStatus, GameMode, Mods
from app.common.config import config_instance as config
from app import cookies

from flask import Blueprint, request, redirect
from flask_login import current_user
from sqlalchemy.orm import Session
from contextlib import suppress

import utils
import app

router = Blueprint('beatmap', __name__)

@router.get('/beatmaps/<id>')
def redirect_to_map(id: int):
    return redirect(f'/b/{id}')

@router.get('/b/<id>')
def get_beatmap(id: str):
    if not id.isdigit():
        return utils.render_error(404, 'beatmap_not_found')

    with app.session.database.managed_session() as session:
        if not (beatmap := beatmaps.fetch_by_id(id, session)):
            return utils.render_error(404, 'beatmap_not_found')

        if beatmap.status <= -3:
            # Beatmap is inactive
            return utils.render_error(404, 'beatmap_not_found')

        if beatmap.beatmapset.explicit and not has_accepted_explicit():
            if request.args.get('explicit') != '1':
                # Beatmap is explicit & user hasn't accepted the warning
                return render_explicit_warning(beatmap)

            # User accepted the warning, remember it & redirect to a regular url
            return accept_explicit(beatmap.id)

        mode = beatmap.mode
        mode_query = request.args.get('mode', '')

        if mode_query.isdigit():
            mode = int(mode_query)

        if mode not in GameMode:
            return redirect(f'/b/{id}')

        if not (mods := request.args.get('mods')):
            mods = ""

        personal_best_rank = None
        personal_best = None
        friend_ids = []

        if current_user.is_authenticated:
            personal_best = scores.fetch_personal_best_score(
                beatmap.id,
                current_user.id,
                int(mode),
                session=session
            )

            personal_best_rank = scores.fetch_score_index(
                current_user.id,
                beatmap.id,
                int(mode),
                session=session
            )

            friend_ids = relationships.fetch_target_ids(
                current_user.id,
                session=session
            )

        beatmap.beatmapset.beatmaps.sort(
            key=lambda x: (x.mode, x.diff)
        )

        beatmap_scores = fetch_beatmap_scores(
            beatmap.id,
            mode=mode,
            mods=mods,
            session=session
        )

        return utils.render_template(
            'beatmap.html',
            css='beatmap.css',
            beatmap=beatmap,
            beatmapset=beatmap.beatmapset,
            mode=mode,
            mods=mods,
            title=f"{beatmap.beatmapset.artist} - {beatmap.beatmapset.title}",
            Status=BeatmapStatus,
            Language=BeatmapLanguage,
            Genre=BeatmapGenre,
            scores=beatmap_scores,
            collaborations=collaborations.fetch_by_beatmap(beatmap.id, session=session),
            collaboration_requests=(
                collaborations.fetch_requests_outgoing(beatmap.id, session=session)
                if current_user.is_authenticated and beatmap.status <= 0 else []
            ),
            favourites_count=beatmap.beatmapset.favourite_count,
            favourites=favourites.fetch_many_by_set(beatmap.set_id, session=session),
            favorite=(
                favourites.fetch_one(current_user.id, beatmap.set_id, session=session)
                if current_user.is_authenticated else None
            ),
            site_title=f"{beatmap.full_name} - Beatmap Info - Titanic!",
            site_description=f"Titanic » Beatmaps » {beatmap.full_name}",
            site_image=f"{config.OSU_BASEURL}/mt/{beatmap.set_id}l.jpg",
            personal_best=personal_best,
            personal_best_rank=personal_best_rank,
            bat_nomination=(
                nominations.fetch_one(beatmap.set_id, current_user.id, session)
                if current_user.is_authenticated else None
            ),
            nominations=nominations.fetch_by_beatmapset(beatmap.set_id, session),
            canonical_url=f'/b/{beatmap.beatmapset.beatmaps[0].id}',
            friends=friend_ids,
            session=session
        )

def fetch_beatmap_scores(
    beatmap_id: int,
    mode: int,
    mods: str,
    session: Session
) -> list[DBScore]:
    mods = mods.strip().removeprefix("+")

    with suppress(ValueError):
        if mods.isdigit():
            return scores.fetch_range_scores_mods(
                beatmap_id,
                mode=mode,
                mods=Mods(int(mods)).value,
                limit=config.SCORE_RESPONSE_LIMIT,
                session=session
            )

        elif mods:
            return scores.fetch_range_scores_mods(
                beatmap_id,
                mode=mode,
                mods=Mods.from_string(mods).value,
                limit=config.SCORE_RESPONSE_LIMIT,
                session=session
            )

    return scores.fetch_range_scores(
        beatmap_id,
        mode=mode,
        limit=config.SCORE_RESPONSE_LIMIT,
        session=session
    )

def has_accepted_explicit() -> bool:
    return request.cookies.get('explicit') == '1'

def render_explicit_warning(beatmap: DBBeatmap):
    mode = request.args.get('mode', '')
    mode_query = f'&mode={mode}' if mode.isdigit() else ''

    return utils.render_template(
        'beatmap_explicit.html',
        css='forums.css', # TODO: refactor css
        beatmap=beatmap,
        beatmapset=beatmap.beatmapset,
        title=f"{beatmap.beatmapset.artist} - {beatmap.beatmapset.title}",
        site_title=f"{beatmap.full_name} - Beatmap Info - Titanic!",
        robots='noindex',
        continue_url=f'/b/{beatmap.id}?explicit=1{mode_query}'
    )

def accept_explicit(beatmap_id: int):
    mode = request.args.get('mode', '')
    redirect_target = f'/b/{beatmap_id}'
    redirect_target += f'?mode={mode}' if mode.isdigit() else ''

    response = redirect(redirect_target)
    response.set_cookie(
        'explicit',
        '1',
        # NOTE: this is cleared when the browser is closed
        secure=cookies.determine_secure(),
        samesite=cookies.determine_samesite()
    )
    return response
