
from __future__ import annotations
from app.common.helpers import caching

import markdown
import config
import app

BASEURL = (
    f'https://raw.githubusercontent.com'
    f'/{config.WIKI_REPOSITORY_OWNER}'
    f'/{config.WIKI_REPOSITORY_NAME}'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

def fetch_languages() -> Set[str]:
    """Fetch the list of available languages"""
    return set(wiki.fetch_languages() + [config.WIKI_DEFAULT_LANGUAGE])

@caching.ttl_cache(ttl=60*5)
def fetch_markdown(path: str, language: str) -> str | None:
    """Fetch the raw markdown text of a wiki page"""
    response = app.session.requests.get(
        f'{config.WIKI_BASEURL}/{path}/{language}.md',
        allow_redirects=True
    )

    if response.ok:
        return response.text

    if language != config.WIKI_DEFAULT_LANGUAGE:
        return fetch_markdown(path, config.WIKI_DEFAULT_LANGUAGE)

    return None

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return markdown.markdown(
        text,
        extensions=['markdown.extensions.tables']
    )
