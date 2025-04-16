
from flask import Blueprint, Response, request, abort
from app.common.database import packs

import utils
import app

router = Blueprint('beatmap-packs', __name__)

@router.get('/')
def pack_listing():
    with app.session.database.managed_session() as session:
        categories = packs.fetch_categories(session)
        category = request.args.get('category', None)
        beatmap_packs = []

        if categories and category is None:
            category = categories[0]
        
        if category:
            beatmap_packs = packs.fetch_by_category(category, session)

        return utils.render_template(
            'packs.html',
            css='packs.css',
            site_description="Titanic » Beatmap Packs",
            site_title="Beatmap Packs",
            title="Beatmap Packs - Titanic",
            canonical_url=request.base_url,
            beatmap_packs=beatmap_packs,
            categories=categories,
            category=category,
            session=session
        )
