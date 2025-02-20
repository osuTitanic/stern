
from flask import Blueprint, request, abort, redirect
from datetime import datetime
from app import wiki

import config
import utils
import app

router = Blueprint('wiki', __name__)
valid_languages = wiki.fetch_languages()

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
        requested_language=language
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
        requested_language=language
    )

@router.get('/<language>/<path:path>')
def wiki_page(path: str, language: str = config.WIKI_DEFAULT_LANGUAGE):
    if language.lower() not in valid_languages:
        return abort(404)

    with app.session.database.managed_session() as session:
        if not (result := wiki.fetch_page(path, language.lower(), session)):
            return abort(404)

        page, entry = result

        return utils.render_template(
            f'wiki/content/{language}.html',
            css='wiki.css',
            content=wiki.process_markdown(entry.content),
            title=f'{page.name} - Titanic! Wiki',
            site_title=f'{page.name} - Titanic! Wiki',
            site_url=f'/wiki/en/{path}',
            canonical_url=f'/wiki/en/{path}',
            requested_language=language,
            language=entry.language
        )
