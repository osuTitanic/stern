
from app.common.constants import BeatmapLanguage, BeatmapGenre, DatabaseStatus, Mods
from app.common.database.repositories import beatmaps, scores, favourites
from flask import Blueprint, request, abort

import flask_login
import config
import utils
import app

router = Blueprint('beatmap', __name__)

@router.get('/<id>')
def get_beatmap(id: int):
    if not id.isdigit():
        return abort(
            code=404,
            description=app.constants.BEATMAP_NOT_FOUND
        )

    with app.session.database.managed_session() as session:
        if not (beatmap := beatmaps.fetch_by_id(id, session)):
            return abort(
                code=404,
                description=app.constants.BEATMAP_NOT_FOUND
            )

        if not (mode := request.args.get('mode')):
            mode = beatmap.mode

        personal_best = None
        personal_best_rank = None

        if not flask_login.current_user.is_anonymous:
            personal_best = scores.fetch_personal_best(
                beatmap.id,
                flask_login.current_user.id,
                int(mode),
                session=session
            )

            personal_best_rank = scores.fetch_score_index(
                flask_login.current_user.id,
                beatmap.id,
                int(mode),
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
            site_image=f"https://assets.ppy.sh/beatmaps/{beatmap.set_id}/covers/list.jpg",
            site_description=f"Titanic » beatmaps » {beatmap.full_name}",
            site_title=f"{beatmap.full_name} - Beatmap Info",
            personal_best=personal_best,
            personal_best_rank=personal_best_rank
        )
