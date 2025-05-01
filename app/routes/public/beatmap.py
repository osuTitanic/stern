
from app.common.database import beatmaps, scores, favourites, nominations, relationships
from app.common.constants import BeatmapLanguage, BeatmapGenre, DatabaseStatus, Mods
from flask import Blueprint, request, redirect
from flask_login import current_user

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

        personal_best = None
        personal_best_rank = None
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
            key=lambda x: x.diff
        )

        beatmap_scores = scores.fetch_range_scores(
            beatmap.id,
            mode=int(mode),
            limit=config.SCORE_RESPONSE_LIMIT,
            session=session
        )

        for score in beatmap_scores:
            mods = Mods(score.mods)

            if Mods.Nightcore in mods:
                score.mods &= ~Mods.DoubleTime

        return utils.render_template(
            'beatmap.html',
            mode=int(mode),
            beatmap=beatmap,
            beatmapset=beatmap.beatmapset,
            css='beatmap.css',
            title=f"{beatmap.beatmapset.artist} - {beatmap.beatmapset.title}",
            Status=DatabaseStatus,
            Language=BeatmapLanguage,
            Genre=BeatmapGenre,
            scores=beatmap_scores,
            favourites_count=favourites.fetch_count_by_set(beatmap.set_id, session=session),
            favourites=favourites.fetch_many_by_set(beatmap.set_id, session=session),
            favorite=(
                favourites.fetch_one(current_user.id, beatmap.set_id, session=session)
                if current_user.is_authenticated else None
            ),
            site_image=f"https://assets.ppy.sh/beatmaps/{beatmap.set_id}/covers/list.jpg",
            site_description=f"Titanic » beatmaps » {beatmap.full_name}",
            site_title=f"{beatmap.full_name} - Beatmap Info",
            personal_best=personal_best,
            personal_best_rank=personal_best_rank,
            bat_error=request.args.get('bat_error'),
            bat_nomination=(
                nominations.fetch_one(beatmap.set_id, current_user.id, session)
                if current_user.is_authenticated else None
            ),
            nominations=nominations.fetch_by_beatmapset(beatmap.set_id, session),
            canonical_url=f'/b/{beatmap.beatmapset.beatmaps[0].id}',
            friends=friend_ids,
            session=session
        )
