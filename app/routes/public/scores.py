
from app.common.constants import GameMode
from app.common.database import scores
from flask import (
    Blueprint,
    send_file,
    redirect,
    abort
)

import app
import io

router = Blueprint('scores', __name__)

@router.get('/<id>')
def get_scores(id: int):
    if not (score := scores.fetch_by_id(id)):
        return abort(404)

    # TODO: Add score page
    return redirect(f'/b/{score.beatmap_id}#{score.id}')

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
