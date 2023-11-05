
from app.common.constants import BeatmapSortBy, BeatmapOrder
from app.common.database.repositories import beatmapsets
from flask import Blueprint, request, redirect

import config
import utils
import app

router = Blueprint('beatmapsets', __name__)

@router.get('/')
def search_beatmap():
    return utils.render_template(
        'search.html',
        css='search.css',
        query=request.args.get('query', default=''),
        sort=request.args.get('sort', default=BeatmapSortBy.Ranked.value, type=int),
        order=request.args.get('order', default=BeatmapOrder.Descending.value, type=int)
    )

@router.get('/<id>')
def redirect_to_set(id: int):
    return redirect(f'/s/{id}')
