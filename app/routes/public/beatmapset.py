
from app.common.constants import BeatmapSortBy, BeatmapOrder
from app.common.database.repositories import beatmapsets
from flask import Response, Blueprint, abort, redirect, request
from flask_login import current_user
from . import packs

import utils
import app

router = Blueprint('beatmapset', __name__)
router.register_blueprint(packs.router, url_prefix='/beatmapsets/packs')

@router.get('/s/<id>')
def get_beatmapset(id: int):
    if not id.isdigit():
        return utils.render_error(404, 'beatmap_not_found')

    with app.session.database.managed_session() as session:
        if not (set := beatmapsets.fetch_one(id, session=session)):
            return utils.render_error(404, 'beatmap_not_found')

        if not set.beatmaps:
            return utils.render_error(404, 'beatmap_not_found')

        if mode := request.args.get('mode', ''):
            mode = f'?mode={mode}'

        beatmap = set.beatmaps[0]

        # Redirect to beatmap based on mode
        available_beatmaps = [
            map for map in set.beatmaps
            if map.mode == request.args.get('mode', 0, type=int)
        ]

        if available_beatmaps:
           beatmap = available_beatmaps[0]

        return redirect(f'/b/{beatmap.id}{mode}')

@router.get('/beatmapsets/')
def beatmap_search():
    return utils.render_template(
        'search.html',
        css='search.css',
        title="Beatmap Listing - Titanic",
        site_title="Beatmap Listing",
        site_description="Search for beatmaps",
        site_image=f"{app.config.OSU_BASEURL}/images/logo/main-low.png",
        canonical_url=request.base_url,
        page=request.args.get('page', default=0, type=int),
        query=request.args.get('query', default="", type=str),
        category=request.args.get('category', default=None, type=int),
        language=request.args.get('language', default=None, type=int),
        genre=request.args.get('genre', default=None, type=int),
        mode=request.args.get('mode', default=None, type=int),
        sort=request.args.get('sort', default=BeatmapSortBy.Ranked, type=int),
        order=request.args.get('order', default=BeatmapOrder.Descending, type=int)
    )

@router.get('/beatmapsets/<id>')
def redirect_to_set(id: str):
    return redirect(f'/s/{id}')

@router.get('/beatmapsets/<set_id>/discussion/<map_id>')
@router.get('/beatmapsets/<set_id>/discussion/')
def redirect_to_discussion(set_id: str, map_id=None):
    if not set_id.isdigit():
        return utils.render_error(404, 'beatmap_not_found')

    if not (set := beatmapsets.fetch_one(set_id)):
        return utils.render_error(404, 'beatmap_not_found')

    if not set.topic_id:
        return redirect(f'/s/{set.id}')

    return redirect(f'/forum/t/{set.topic_id}')

@router.get('/beatmapsets/download/<id>')
def download_beatmapset(id: str):
    if not id.isdigit():
        return abort(code=404)

    if current_user.is_anonymous:
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

    # no_video can only be true if the beatmapset has videos
    no_video = (
        no_video and set.has_video
    )

    response = app.session.storage.api.osz(
        set.id,
        no_video
    )

    if not response:
        return abort(code=404)

    estimated_size = (
        set.osz_filesize_novideo if no_video else
        set.osz_filesize
    )

    osz_filename = utils.secure_filename(f'{set.id} {set.artist} - {set.title}')
    osz_filename += ' (no video)' if no_video else ''
    osz_filename += '.osz'

    return Response(
        response.iter_content(65536),
        mimetype='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename="{osz_filename}";',
            'Content-Length': response.headers.get('Content-Length', f"{estimated_size}"),
            'Last-Modified': set.last_update.strftime('%a, %d %b %Y %H:%M:%S GMT')
        }
    )
