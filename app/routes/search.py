
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
        query=request.args.get('query', default='')
    )

@router.get('/<id>')
def redirect_to_set(id: int):
    return redirect(f'/s/{id}')
