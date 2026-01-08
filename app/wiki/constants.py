
from app.common.config import config_instance as config
import re

__all__ = [
    'GITHUB_BASEURL',
    'BLOB_BASEURL',
    'HISTORY_BASEURL',
    'CREATE_BASEURL',
    'CONTENT_BASEURL',
    'LINK_REGEX',
    'LANGUAGES',
    'LANGUAGE_NAMES'
]

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

CREATE_BASEURL = (
    f'{GITHUB_BASEURL}/new'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

CONTENT_BASEURL = (
    f'https://raw.githubusercontent.com'
    f'/{config.WIKI_REPOSITORY_OWNER}'
    f'/{config.WIKI_REPOSITORY_NAME}/refs/heads'
    f'/{config.WIKI_REPOSITORY_BRANCH}'
    f'/{config.WIKI_REPOSITORY_PATH}'
)

LINK_REGEX = re.compile(
    r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]"
)

WIKI_LINK_REGEX = re.compile(
    r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]"
)

LANGUAGES = (
    'en', 'ru', 'de', 'pl', 'fi', 'et', 'fr'
)

LANGUAGE_NAMES = {
    'en': 'English',
    'ru': 'Русский',
    'de': 'Deutsch',
    'pl': 'Polski',
    'fi': 'Suomi',
    'et': 'Eesti',
    'fr': 'Français'
}
