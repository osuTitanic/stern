
from flask import Blueprint, Response, request, redirect, abort
from app.common.constants import BeatmapSortBy, BeatmapOrder
from app.common.database.repositories import beatmapsets
from . import packs

import flask_login
import unicodedata
import utils
import app
import re

router = Blueprint('beatmapsets', __name__)
router.register_blueprint(packs.router, url_prefix='/packs')

@router.get('/')
def search_beatmap():
    return utils.render_template(
        'search.html',
        css='search.css',
        title="Beatmap Listing - Titanic",
        site_title="Beatmaps Listing",
        site_description="Search for beatmaps",
        canonical_url=request.base_url,
        page=request.args.get('page', default=0, type=int),
        query=request.args.get('query', default="", type=str),
        category=request.args.get('category', default=None, type=int),
    )

def secure_filename(filename: str) -> str:
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    filename = re.compile(r"[^A-Za-z0-9_.-]").sub(" ", filename)
    filename = re.compile(r"\s+").sub(" ", filename)
    return filename.strip()

@router.get('/download/<id>')
def download_beatmapset(id: int):
    if not id.isdigit():
        return abort(code=404)

    if flask_login.current_user.is_anonymous:
        return abort(code=404)

    if not (set := beatmapsets.fetch_one(id)):
        return abort(code=404)

    if not set.available:
        return abort(code=451)

    no_video = request.args.get(
        'novideo',
        default=False,
        type=bool
    )

    response = app.session.storage.api.osz(
        set.id,
        no_video
    )

    if not response:
        return abort(code=404)

    osz_filename = secure_filename(
        f'{set.id} {set.artist} - {set.title}'
    ) + '.osz'

    return Response(
        response.iter_content(6400),
        mimetype='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename={osz_filename}',
            'Content-Length': response.headers.get('Content-Length', 0)
        }
    )

@router.get('/<id>')
def redirect_to_set(id: int):
    return redirect(f'/s/{id}')
