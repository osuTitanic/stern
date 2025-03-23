
from __future__ import annotations
from app.common.database import DBWikiPage, DBWikiContent, wiki
from app.wiki.constants import CONTENT_BASEURL, LINK_REGEX
from app.common.helpers import caching
from typing import Set, Tuple, List
from sqlalchemy.orm import Session

import logging
import config
import app

logger = logging.getLogger("wiki")

def fetch_page(path: str, language: str, session: Session) -> Tuple[DBWikiPage, DBWikiContent] | None:
    """Fetch a wiki page, or create it if it doesn't exist"""
    if not (page := wiki.fetch_page_by_name(get_page_name(path), session)):
        logger.info(f"Page '{path}' not found in database, creating...")
        return create_page(path, language, session)

    default_content = wiki.fetch_content(
        page.id,
        config.WIKI_DEFAULT_LANGUAGE,
        session=session
    )

    if not default_content:
        logger.error(f"Default content for page '{path}' not found, recreating...")
        wiki.delete_outlinks(page.id, session)
        wiki.delete_page(page.id, session)
        return create_page(path, language, session)

    if language == config.WIKI_DEFAULT_LANGUAGE:
        return page, update_content(default_content, session)

    if not (content := wiki.fetch_content(page.id, language, session)):
        # Try to create content in the requested language
        content_markdown = fetch_markdown_cached(path, language)

        if not content_markdown:
            return page, default_content
        
        content = wiki.create_content_entry(
            page.id,
            parse_title(content_markdown),
            content_markdown,
            language,
            session=session
        )
        return page, content
    
    return page, update_content(content, session)

@caching.ttl_cache(ttl=60*5)
def fetch_markdown_cached(path: str, language: str) -> str | None:
    """Fetch the raw markdown text of a wiki page, with caching"""
    return fetch_markdown(path, language)

def fetch_markdown(path: str, language: str) -> str | None:
    """Fetch the raw markdown text of a wiki page"""
    response = app.session.requests.get(
        f'{CONTENT_BASEURL}/{path.replace(" ", "_")}/{language}.md',
        allow_redirects=True
    )

    if response.ok:
        logger.debug(f"Received markdown response ({len(response.text)} bytes)")
        return sanitize_markdown(response.text)

    logger.error(f"Failed to fetch markdown '{response.url}' ({response.status_code})")
    return None

def create_page(path: str, language: str, session: Session) -> Tuple[DBWikiPage, DBWikiContent] | None:
    """Create a wiki page"""
    logger.info(f"Creating page '{path}' in language '{language}'")

    # Check if page is available in default language
    default_content_markdown = fetch_markdown_cached(
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
    content_markdown = fetch_markdown_cached(path, language)

    if not content_markdown:
        logger.info(f"Page '{path}' is only available in default language")
        return page, default_content
    
    logger.info(
        f"Creating content in language '{language}'"
    )

    content = wiki.create_content_entry(
        page.id,
        parse_title(content_markdown),
        content_markdown,
        language,
        session=session
    )

    return page, content

def update_content(entry: DBWikiContent, session: Session, no_cache: bool = False) -> DBWikiContent:
    """Update the content of a wiki page"""
    markdown_resolver = (
        fetch_markdown_cached
        if not no_cache else fetch_markdown
    )

    content_markdown = markdown_resolver(
        entry.page.name,
        entry.language
    )

    if not content_markdown:
        # Content was deleted -> remove entry & page
        wiki.delete_outlinks(entry.page_id, session)
        wiki.delete_content(entry.page_id, session)
        wiki.delete_page(entry.page_id, session)
        return entry

    if content_markdown == entry.content:
        return entry

    wiki.update_content(
        entry.page_id,
        entry.language,
        content_markdown,
        parse_title(content_markdown),
        session=session
    )

    create_outlinks(
        entry.page_id,
        content_markdown,
        session=session
    )

    entry.content = content_markdown
    return entry

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

def get_page_name(path: str) -> str:
    """Get the name of the page from the path"""
    return path.removesuffix('/').split('/')[-1] \
               .removesuffix('.md').replace('_', ' ') \
               .title()

def sanitize_markdown(text: str) -> str:
    """Sanitize markdown text"""
    return text.encode().strip() \
        .strip(b'\xef\xbb\xbf') \
        .strip(b'\ufeff').strip(b'\n') \
        .decode('utf-8')

def parse_title(text: str) -> str:
    """Parse the title of a wiki page"""
    return text.split('\n')[0].lstrip('#').strip()
