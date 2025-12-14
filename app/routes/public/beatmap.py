
from app.common.database import beatmaps, scores, favourites, nominations, relationships, collaborations
from app.common.constants import BeatmapLanguage, BeatmapGenre, BeatmapStatus, Mods
from flask import Blueprint, request, redirect
from flask_login import current_user
from sqlalchemy.orm import Session
from contextlib import suppress

import config
import utils
import app

router = Blueprint('beatmap', __name__)

@router.get('/beatmaps/<id>')
def redirect_to_map(id: int):
    return redirect(f'/b/{id}')

@router.get('/b/<id>')
def get_beatmap(id: int):
    if not id.isdigit():
        return utils.render_error(404, 'beatmap_not_found')

    with app.session.database.managed_session() as session:
        if not (beatmap := beatmaps.fetch_by_id(id, session)):
            return utils.render_error(404, 'beatmap_not_found')

        if beatmap.status <= -3:
            # Beatmap is inactive
            return utils.render_error(404, 'beatmap_not_found')

        if not (mode := request.args.get('mode')):
            mode = beatmap.mode

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
            mode=int(mode),
            mods=mods,
            session=session
        )

        return utils.render_template(
            'beatmap.html',
            css='beatmap.css',
            beatmap=beatmap,
            beatmapset=beatmap.beatmapset,
            mode=int(mode),
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
            favourites_count=favourites.fetch_count_by_set(beatmap.set_id, session=session),
            favourites=favourites.fetch_many_by_set(beatmap.set_id, session=session),
            favorite=(
                favourites.fetch_one(current_user.id, beatmap.set_id, session=session)
                if current_user.is_authenticated else None
            ),
            site_title=f"{beatmap.full_name} - Beatmap Info",
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
    mode: int | None,
    mods: str,
    session: Session
) -> None:
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
