
from flask import Blueprint, Response, abort
from app.common.database import packs

import utils
import app

router = Blueprint('beatmap-packs', __name__)

@router.get('/')
def pack_listing():
    return utils.render_template(
        'packs.html',
        css='packs.css',
        site_description="Titanic » Beatmap Packs",
        site_title="Beatmap Packs",
        title="Beatmap Packs - Titanic",
        categories=packs.fetch_categories(),
    )
