
from app.common.database import releases
from collections import defaultdict
from flask import Blueprint

import utils

router = Blueprint('download', __name__)

@router.get('/')
def download():
    client_releases = releases.fetch_all()
    sorted_releases = defaultdict(list)

    for release in client_releases:
        sorted_releases[release.category].append(release)

    return utils.render_template(
        'download.html',
        css='download.css',
        title="Download - Titanic",
        site_title="Download",
        site_description="Let's get you started! Choose and download your preferred version of osu!.",
        releases=sorted_releases
    )
