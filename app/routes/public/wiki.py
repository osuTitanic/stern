
from flask import Blueprint, request, abort, redirect
from datetime import datetime
from app import wiki

import config
import utils

router = Blueprint('wiki', __name__)

valid_languages = (
    'bg', 'cs', 'de', 'en',
    'es', 'fr', 'id', 'it',
    'ja', 'ko', 'pl', 'pt-br',
    'ro', 'ru', 'sv', 'th',
    'tr', 'uk', 'vi', 'zh', 'zh-tw'
)

@router.get('/')
def wiki_home_redirect():
    return redirect('/wiki/en/')

@router.get('/<language>/')
def home_wiki_page(language: str):
    if language.lower() not in valid_languages:
        return abort(404)

    return utils.render_template(
        f'wiki/home/{language.lower()}.html',
        css='wiki.css',
        title='Home - Titanic! Wiki',
        site_title='Titanic! Wiki',
        canonical_url=f'/wiki/',
        current_date=datetime.now(),
        language=language
    )

@router.get('/<language>/search/')
def wiki_search_page(language: str):
    if language.lower() not in valid_languages:
        return abort(404)

    query = request.args.get('query', None)

    # TODO: Implement search functionality
    return utils.render_template(
        f'wiki/search/{language.lower()}.html',
        css='wiki.css',
        title=f'{query or "Search"} - Titanic! Wiki',
        site_title='Titanic! Wiki',
        canonical_url=f'/wiki/en/search',
        language=language
    )

@router.get('/<language>/<path:path>')
def wiki_page(path: str, language: str = config.WIKI_DEFAULT_LANGUAGE):
    if language.lower() not in valid_languages:
        return abort(404)

    if not (text := wiki.fetch_markdown(path, language.lower())):
        return abort(404)

    name = (
        path.strip('/').split('/')[-1]
    )

    return utils.render_template(
        f'wiki/content/{language}.html',
        css='wiki.css',
        content=wiki.process_markdown(text),
        title=f'{name} - Titanic! Wiki',
        site_title=f'{name} - Titanic! Wiki',
        site_url=f'/wiki/en/{path}',
        canonical_url=f'/wiki/en/{path}',
        language=language
    )
