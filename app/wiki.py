
from __future__ import annotations
from app.common.database import DBWikiPage, DBWikiContent, wiki
from app.common.helpers import caching
from typing import Set, Tuple, List
from sqlalchemy.orm import Session

import markdown
import logging
import config
import app
import re

GITHUB_BASEURL = (
    f'https://github.com'
    f'/{config.WIKI_REPOSITORY_OWNER}'
    f'/{config.WIKI_REPOSITORY_NAME}'
)

BLOB_BASEURL = (
    f'{GITHUB_BASEURL}/blob'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

HISTORY_BASEURL = (
    f'{GITHUB_BASEURL}/commits'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

CONTENT_BASEURL = (
    f'https://raw.githubusercontent.com'
    f'/{config.WIKI_REPOSITORY_OWNER}'
    f'/{config.WIKI_REPOSITORY_NAME}'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

LINK_REGEX = re.compile(
    r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]"
)

logger = logging.getLogger("wiki")

def fetch_page(path: str, language: str, session: Session) -> Tuple[DBWikiPage, DBWikiContent] | None:
    """Fetch a wiki page, or create it if it doesn't exist"""
    if not (page := wiki.fetch_page_by_name(get_page_name(path), session)):
        logger.info(f"Page '{path}' not found in database, creating...")
        return create_page(path, language, session)

    default_content = wiki.fetch_content(
        page.id,
        config.WIKI_DEFAULT_LANGUAGE,
        session
    )

    if language == config.WIKI_DEFAULT_LANGUAGE:
        return page, update_content(default_content, session)

    if not (content := wiki.fetch_content(page.id, language, session)):
        # Try to create content in the requested language
        content_markdown = fetch_markdown(path, language)

        if not content_markdown:
            return page, default_content
        
        content = wiki.create_content_entry(
            page.id,
            content_markdown,
            language,
            session=session
        )
        return page, content
    
    return page, update_content(content, session)

def fetch_languages() -> Set[str]:
    """Fetch the list of available languages"""
    return set(wiki.fetch_languages() + [config.WIKI_DEFAULT_LANGUAGE])

@caching.ttl_cache(ttl=60*5)
def fetch_markdown(path: str, language: str) -> str | None:
    """Fetch the raw markdown text of a wiki page"""
    response = app.session.requests.get(
        f'{CONTENT_BASEURL}/{path}/{language}.md',
        allow_redirects=True
    )

    if response.ok:
        logger.debug(f"Received markdown response ({len(response.text)} bytes)")
        return response.text

    logger.error(f"Failed to fetch markdown '{response.url}' ({response.status_code})")
    return None

def create_page(path: str, language: str, session: Session) -> Tuple[DBWikiPage, DBWikiContent] | None:
    """Create a wiki page"""
    logger.info(f"Creating page '{path}' in language '{language}'")

    # Check if page is available in default language
    default_content_markdown = fetch_markdown(
        path, config.WIKI_DEFAULT_LANGUAGE
    )

    if not default_content_markdown:
        logger.error(f"Page '{path}' not found in default language")
        return None

    page, default_content = wiki.create_page(
        get_page_name(path),
        default_content_markdown,
        config.WIKI_DEFAULT_LANGUAGE,
        session=session
    )

    logger.info(
        f"Page '{path}' created in default language"
    )

    create_outlinks(
        page.id,
        default_content_markdown,
        session=session
    )

    if language == config.WIKI_DEFAULT_LANGUAGE:
        return page, default_content

    # Check if page is available in requested language
    content_markdown = fetch_markdown(path, language)

    if not content_markdown:
        logger.info(f"Page '{path}' is only available in default language")
        return page, default_content
    
    logger.info(
        f"Creating content in language '{language}'"
    )

    content = wiki.create_content_entry(
        page.id,
        content_markdown,
        language,
        session=session
    )

    return page, content

def update_content(content: DBWikiContent, session: Session) -> DBWikiContent:
    """Update the content of a wiki page"""
    content_markdown = fetch_markdown(
        content.page.name,
        content.language
    )

    if not content_markdown:
        return content

    if content.content == content_markdown:
        return content

    wiki.update_content(
        content.page_id,
        content.language,
        content_markdown,
        session
    )

    create_outlinks(content.page_id, content_markdown, session)
    content.content = content_markdown
    return content

def create_outlinks(page_id: int, content: str, session: Session) -> List[DBWikiPage]:
    """Scan for outlinks, and return associated pages"""
    outlinks = LINK_REGEX.findall(content)
    logger.info(f'Found {len(outlinks)} outlinks.')

    pages = [
        page[0] for match in outlinks
        if (page := fetch_page(match[0], config.WIKI_DEFAULT_LANGUAGE, session))
    ]

    wiki.delete_outlinks(
        page_id,
        session
    )

    for target in pages:
        wiki.create_outlink(
            page_id,
            target.id,
            session
        )

    return pages

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return markdown.markdown(
        text,
        extensions=['markdown.extensions.tables']
    )

def get_page_name(path: str) -> str:
    """Get the name of the page from the path"""
    return path.removesuffix('/').split('/')[-1] \
               .removesuffix('.md').replace('_', ' ') \
               .title()
