
from app.common.database.repositories import scores
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
    replay_data = app.session.storage.get_full_replay(id)

    if not replay_data:
        return redirect('about:blank')

    return send_file(
        io.BytesIO(replay_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=f'{id}.osr'
    )
