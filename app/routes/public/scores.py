
from flask import Blueprint, send_file, redirect, abort
from app.common.constants import GameMode
from app.common.database import scores

import config
import utils
import app
import io

router = Blueprint("scores", __name__)

@router.get("/<id>", strict_slashes=False)
def get_score(id: int):
    """Render individual score page"""

    if not str(id).isdigit():
        return abort(404)

    with app.session.database.managed_session() as session:
        if not (score := scores.fetch_by_id(int(id), session)):
            return abort(404)

        if score.hidden:
            return abort(404)

        if not score.passed:
            return abort(404)

        score_rank = scores.fetch_score_index_by_id(
            score.id,
            score.beatmap_id,
            score.mode,
            session=session
        )

        user = score.user
        user.stats.sort(key=lambda s: s.mode)
        beatmap = score.beatmap
        beatmapset = beatmap.beatmapset

        site_title = (
            f"Titanic » {beatmapset.artist} - {beatmapset.title} » {user.name}'s Score"
        )
        site_description = (
            f"{user.name} achieved #{score_rank} with "
            f"{score.acc * 100:.2f}% ({score.grade}) for {score.pp:.2f}pp "
            f"on {beatmap.full_name}"
        )
        site_image = f"{config.OSU_BASEURL}/mt/{beatmap.set_id}l.jpg"

        return utils.render_template(
            "score.html",
            user=user,
            score=score,
            beatmap=beatmap,
            beatmapset=beatmapset,
            css="scores.css",
            site_title=site_title,
            site_description=site_description,
            site_image=site_image,
            score_rank=score_rank,
            title=site_title,
        )

@router.get('/<id>/download')
def download_replay(id: int):
    with app.session.database.managed_session() as session:
        if not (score := scores.fetch_by_id(id, session)):
            return abort(404)

        if not (replay := app.session.storage.get_full_replay_from_score(score)):
            return redirect('about:blank')

        formatted_time = score.submitted_at.strftime("%Y-%m-%d %H-%M-%S")
        mode = GameMode(score.mode).name

        return send_file(
            io.BytesIO(replay),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'{score.user.name} - {score.beatmap.full_name} ({formatted_time}) {mode}.osr'
        )
