
from __future__ import annotations
from app.common.helpers import caching

import markdown
import config
import app

@caching.ttl_cache(ttl=300)
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
