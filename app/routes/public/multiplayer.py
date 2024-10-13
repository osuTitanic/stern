
from app.common.database.repositories import matches
from flask import Blueprint, Response, abort

import utils
import app

router = Blueprint('multiplayer', __name__)

@router.get('/<id>')
def get_match(id: int):
    with app.session.database.managed_session() as session:
        if not (match := matches.fetch_by_id(id, session=session)):
            return abort(404)

        return utils.render_template(
            'match.html',
            css='match.css',
            match=match,
            site_description=f"Titanic » Matches » {match.name} (#{match.id:02d})",
            site_title=f"{match.name}",
            title=f"{match.name} - Titanic"
        )
