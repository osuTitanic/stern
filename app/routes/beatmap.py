
from app.common.constants import BeatmapLanguage, BeatmapGenre, DatabaseStatus
from app.common.database.repositories import beatmaps, scores, favourites
from flask import Blueprint, request, abort

import config
import utils

router = Blueprint('beatmap', __name__)

@router.get('/<id>')
def get_beatmap(id: int):
    if not (beatmap := beatmaps.fetch_by_id(id)):
        return abort(404)

    if not (mode := request.args.get('m')):
        mode = beatmap.mode

    beatmap.beatmapset.beatmaps.sort(
        key=lambda x: x.diff
    )

    return utils.render_template(
        'beatmap.html',
        mode=int(mode),
        beatmap=beatmap,
        beatmapset=beatmap.beatmapset,
        css='beatmap.css',
        Status=DatabaseStatus,
        Language=BeatmapLanguage,
        Genre=BeatmapGenre,
        scores=scores.fetch_range_scores(
            beatmap.id,
            mode=int(mode),
            limit=config.SCORE_RESPONSE_LIMIT
        ),
        favourites_count=favourites.fetch_count_by_set(beatmap.set_id),
        favourites=favourites.fetch_many_by_set(beatmap.set_id),
        domain=config.DOMAIN_NAME
    )
