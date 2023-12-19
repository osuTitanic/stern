
from flask import Blueprint, Response, request, redirect, abort
from app.common.constants import BeatmapSortBy, BeatmapOrder
from app.common.database.repositories import beatmapsets

import utils
import app

router = Blueprint('beatmapsets', __name__)

@router.get('/')
def search_beatmap():
    page = request.args.get('page', default=0, type=int)
    max_page_display = max(page, min(page, page + 8))
    min_page_display = max(0, min(page, max_page_display - 9))

    arguments = '&'.join([
        f'{key}={value}'
        for key, value in
        request.args.items()
        if key != 'page'
    ])

    if page > 1000: return redirect(f'?page=1000&{arguments}')
    elif page < 0: return redirect(f'?page=0&{arguments}')

    return utils.render_template(
        'search.html',
        css='search.css',
        title="Beatmap Listing - Titanic",
        query=request.args.get('query', default=''),
        sort=request.args.get('sort', default=BeatmapSortBy.Ranked.value, type=int),
        order=request.args.get('order', default=BeatmapOrder.Descending.value, type=int),
        max_page_display=max_page_display,
        min_page_display=min_page_display,
        arguments=arguments,
        page=page
    )

@router.get('/download/<id>')
def download_beatmapset(id: int):
    if not id.isdigit():
        return abort(code=404)

    if not (set := beatmapsets.fetch_one(id)):
        return abort(code=404)

    response = app.session.storage.api.osz(
        set_id=id,
        no_video=request.args.get('novideo', False, type=bool)
    )

    if not response:
        return abort(code=500)

    return Response(
        response.content,
        content_type=response.headers,
        headers={
            'Content-Disposition': f'attachment; filename="{set.id} {set.artist} - {set.title}.osz"',
        }
    )

@router.get('/<id>')
def redirect_to_set(id: int):
    return redirect(f'/s/{id}')
