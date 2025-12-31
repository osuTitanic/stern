
from app.common.database.repositories import changelog
from flask import Blueprint, redirect, request, render_template
from datetime import datetime

import utils
import app

router = Blueprint('changelog', __name__)

client_cutoff = datetime(2015, 12, 30)
client_cutoff_osume = datetime(2012, 6, 1)

@router.get('/p/changelog')
def osu_changelog():
    updater = request.args.get(
        'updater',
        default=0,
        type=int
    )

    match updater:
        case 3:
            return client_changelog()
        case 2:
            return osume_changelog(test=True)
        case 1:
            return osume_changelog()
        case _:
            return redirect('/changelog')

def osume_changelog(limit: int = 50, test: bool = False) -> str:
    with app.session.database.managed_session() as session:
        return render_template(
            'changelog_osume.html',
            entries=changelog.fetch_range_desc(
                client_cutoff_osume,
                limit=limit,
                session=session
            ),
            session=session,
            test=test
        )

def client_changelog() -> str:
    ...
