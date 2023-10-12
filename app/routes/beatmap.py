
from app.common.database.repositories import beatmaps
from flask import (
    render_template,
    Blueprint,
    request,
    abort
)

router = Blueprint('beatmap', __name__)

@router.get('/<id>')
def get_beatmap(id: int):
    if not (beatmap := beatmaps.fetch_by_id(id)):
        return abort(404)

    if not (mode := request.args.get('m')):
        mode = beatmap.mode

    return render_template(
        'beatmap.html',
        beatmap=beatmap,
        beatmapset=beatmap.beatmapset,
        css='beatmap.css',
        mode=mode
    )
