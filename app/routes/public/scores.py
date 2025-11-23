
from flask import Blueprint, send_file, redirect, abort
from app.common.constants import GameMode
from app.common.database import scores
import app
import utils
import config
import requests
import io

router = Blueprint("scores", __name__)


@router.get("/<id>", strict_slashes=False)
def get_score(id: int):
    if not id.isdigit():
        return abort(404)

    try:
        response = requests.get(f"{config.API_BASEURL}/scores/{id}", timeout=5)
    except requests.RequestException:
        return utils.render_error(500, "api_unreachable")

    if response.status_code != 200:
        return abort(404)

    data = response.json()
    score = data
    beatmap = data["beatmap"]
    beatmapset = beatmap["beatmapset"]
    user = data["user"]

    site_title = (
        f"{user['name']} on {beatmapset['artist']} - {beatmapset['title']} "
        f"[{beatmap['version']}] | Titanic"
    )
    site_description = (
        f"{user['name']} achieved {score['pp']:.2f}pp with "
        f"{score['acc'] * 100:.2f}% accuracy ({score['grade']}) on "
        f"{beatmapset['artist']} - {beatmapset['title']} [{beatmap['version']}]"
    )
    site_image = f"{config.OSU_BASEURL}/mt/{beatmap['set_id']}l.jpg"

    return utils.render_template(
        "score.html",
        score=score,
        beatmap=beatmap,
        beatmapset=beatmapset,
        user=user,
        css="beatmap.css",
        site_title=site_title,
        site_description=site_description,
        site_image=site_image,
        title=site_title,
    )


@router.get("/<id>/download")
def download_replay(id: int):
    with app.session.database.managed_session() as session:
        if not (score := scores.fetch_by_id(id, session)):
            return abort(404)

        if not (replay := app.session.storage.get_full_replay_from_score(score)):
            return redirect("about:blank")

        formatted_time = score.submitted_at.strftime("%Y-%m-%d %H-%M-%S")
        mode = GameMode(score.mode).name

        return send_file(
            io.BytesIO(replay),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=f"{score.user.name} - {score.beatmap.full_name} ({formatted_time}) {mode}.osr",
        )



