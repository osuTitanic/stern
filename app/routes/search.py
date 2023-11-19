
from flask import Blueprint, Response, request, redirect, abort
from app.common.constants import BeatmapSortBy, BeatmapOrder
from app.common.database.repositories import beatmapsets

import flask_login
import utils
import app

router = Blueprint('beatmapsets', __name__)

@router.get('/')
def search_beatmap():
    return utils.render_template(
        'search.html',
        css='search.css',
        title="Beatmap Listing - osu!Titanic",
        query=request.args.get('query', default=''),
        sort=request.args.get('sort', default=BeatmapSortBy.Ranked.value, type=int),
        order=request.args.get('order', default=BeatmapOrder.Descending.value, type=int)
    )

@router.get('/download/<id>')
def download_beatmapset(id: int):
    if not id.isdigit():
        return abort(code=404)

    if flask_login.current_user.is_anonymous:
        return abort(code=404)

    if not (set := beatmapsets.fetch_one(id)):
        return abort(code=404)

    no_video = request.args.get('novideo', False, type=bool)

    # Redirect to osu.direct, to reduce server impact
    return redirect(f"https://osu.direct/d/{set.id}{'?noVideo=' if no_video else ''}")

@router.get('/<id>')
def redirect_to_set(id: int):
    return redirect(f'/s/{id}')
