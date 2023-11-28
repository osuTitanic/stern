
from flask import Blueprint

import utils

router = Blueprint('download', __name__)

@router.get('/')
def download():
    return utils.render_template(
        'download.html',
        css='download.css',
        title="Download - Titanic"
    )
