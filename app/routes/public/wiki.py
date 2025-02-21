
from flask import Blueprint, request, abort, redirect
from datetime import datetime
from app import wiki

import config
import utils
import app

router = Blueprint('wiki', __name__)

@router.get('/')
def wiki_home_redirect():
    return redirect('/wiki/en/')

@router.get('/<language>/')
def home_wiki_page(language: str):
    if language.lower() not in wiki.LANGUAGES:
        return abort(404)

    return utils.render_template(
        f'wiki/home/{language.lower()}.html',
        css='wiki.css',
        title='Home - Titanic! Wiki',
        site_title='Titanic! Wiki',
        canonical_url=f'/wiki/',
        current_date=datetime.now(),
        source_url=wiki.GITHUB_BASEURL,
        discussion_url=f'{wiki.GITHUB_BASEURL}/pulls',
        history_url=wiki.HISTORY_BASEURL,
        available_languages=wiki.LANGUAGE_NAMES,
        requested_language=language,
        language=language
    )

@router.get('/<language>/search/')
def wiki_search_page(language: str):
    if language.lower() not in wiki.LANGUAGES:
        return abort(404)

    query = request.args.get('query', None)

    # TODO: Implement search functionality
    return utils.render_template(
        f'wiki/search/{language.lower()}.html',
        css='wiki.css',
        title=f'{query or "Search"} - Titanic! Wiki',
        site_title='Titanic! Wiki',
        canonical_url=f'/wiki/en/search',
        requested_language=language,
        language=language,
        search_query=query
    )

@router.get('/<language>/<path>')
def wiki_page(path: str, language: str = config.WIKI_DEFAULT_LANGUAGE):
    if language.lower() not in wiki.LANGUAGES:
        return abort(404)

    with app.session.database.managed_session() as session:
        if not (result := wiki.fetch_page(path, language.lower(), session)):
            return abort(404)

        page, entry = result

        return utils.render_template(
            f'wiki/content/{language}.html',
            css='wiki.css',
            content=wiki.process_markdown(entry.content),
            title=f'{entry.title} - Titanic! Wiki',
            site_title=f'{entry.title} - Titanic! Wiki',
            site_url=f'/wiki/en/{path}',
            canonical_url=f'/wiki/en/{path}',
            requested_language=language,
            language=entry.language,
            translation_url=f'{wiki.CREATE_BASEURL}/{path}',
            source_url=f'{wiki.BLOB_BASEURL}/{path}/{entry.language}.md',
            history_url=f'{wiki.HISTORY_BASEURL}/{path}/{entry.language}.md',
            discussion_url=f'{wiki.GITHUB_BASEURL}/pulls?q={page.name}'
        )
