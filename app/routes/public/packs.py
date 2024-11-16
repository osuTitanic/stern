
from flask import Blueprint, Response, request, abort
from app.common.database import packs

import utils
import app

router = Blueprint('beatmap-packs', __name__)

@router.get('/')
def pack_listing():
    categories = packs.fetch_categories()
    category = request.args.get('category', None)

    if categories and category is None:
        category = categories[0]

    return utils.render_template(
        'packs.html',
        css='packs.css',
        site_description="Titanic » Beatmap Packs",
        site_title="Beatmap Packs",
        title="Beatmap Packs - Titanic",
        categories=categories,
        category=category
    )
