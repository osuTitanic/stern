
from app.common.database import releases
from flask import Blueprint

import utils

router = Blueprint('download', __name__)

@router.get('/')
def download():
    return utils.render_template(
        'download.html',
        css='download.css',
        title="Download - Titanic",
        site_title="Download",
        site_description="Let's get you started! Choose and download your preferred version of osu!.",
        releases=releases.fetch_all()
    )
