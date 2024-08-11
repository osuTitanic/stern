
from flask import Blueprint, request, abort
from app import wiki

import config
import utils

router = Blueprint('wiki', __name__)

@router.get('/')
def home_wiki_page():
    language = request.args.get(
        'lang',
        config.WIKI_DEFAULT_LANGUAGE
    )

    if not (text := wiki.fetch_markdown('/', language)):
        return abort(404)

    return utils.render_template(
        'wiki.html',
        css='wiki.css',
        title='Home - Titanic! Wiki',
        content=wiki.process_markdown(text)
    )

@router.get('/<path:path>')
def wiki_page(path: str):
    language = request.args.get(
        'lang',
        config.WIKI_DEFAULT_LANGUAGE
    )

    if not (text := wiki.fetch_markdown(path, language)):
        return abort(404)

    name = (
        path.strip('/').split('/')[-1]
    )

    return utils.render_template(
        'wiki.html',
        css='wiki.css',
        title=f'{name} - Titanic! Wiki',
        content=wiki.process_markdown(text)
    )
