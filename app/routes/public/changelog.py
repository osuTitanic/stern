
from app.common.database.repositories import changelog, releases
from app.common.database.objects import DBReleaseChangelog

from flask import Response, Blueprint, redirect, request, render_template
from collections import defaultdict
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
        entries = changelog.fetch_range_desc(
            resolve_target_date(default=client_cutoff_osume),
            limit=limit,
            session=session
        )

        return render_template(
            'changelog_osume.html',
            config=app.session.config,
            entries=entries,
            session=session,
            test=test
        )

def client_changelog() -> Response:
    with app.session.database.managed_session() as session:
        changelog_entries = changelog.fetch_range_desc(
            resolve_target_date(default=client_cutoff),
            session=session
        )

        sorted_entries: dict[datetime, list[DBReleaseChangelog]] = defaultdict(list)

        for entry in changelog_entries:
            date_key = entry.created_at
            sorted_entries[date_key].append(entry)

        result = "\n".join(
            format_entries(date, entries)
            for date, entries in sorted_entries.items()
        )
        return Response(
            result,
            mimetype='text/plain'
        )

def format_entries(date: datetime, entries: list[DBReleaseChangelog]) -> str:
    commits = (
        f"{entry.type_symbol}\t{entry.author}\t{entry.prefixed_text}"
        for entry in entries
    )
    return (
        f"({date.month}/{date.day}/{date.year})\n" +
        "\n".join(commits)
    )

def resolve_target_date(default: datetime) -> datetime:
    from_version = request.args.get(
        'from',
        default=0,
        type=float
    )
    current_version = request.args.get(
        'current',
        default=0,
        type=float
    )

    current_version_string = str(round(current_version))
    version_date = default

    if len(current_version_string) >= 8:
        version_date = datetime(
            int(current_version_string[0:4]),
            int(current_version_string[4:6]),
            int(current_version_string[6:8])
        )

    return version_date
