
from app.wiki.extensions import WikiLinks
from markdown import Markdown

MarkdownInstance = Markdown(
    extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.abbr',
        'markdown.extensions.footnotes',
        'markdown.extensions.meta',
        'app.wiki.extensions.wikilinks',
    ],
    extension_configs={
        'markdown.extensions.toc': {
            'title': 'Contents',
            'marker': '[TOC]',
        },
        'markdown.extensions.footnotes': {
            'PLACE_MARKER': '// Footnotes //',
        },
        'app.wiki.extensions.wikilinks': {
            'base_url': '/wiki/',
            'end_url': '',
            'html_class': 'wikilink',
            'build_url': WikiLinks.buildUrl,
        }
    }
)

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return MarkdownInstance.convert(text)

def insert_toc(text: str) -> str:
    """Insert a table of contents into the text"""
    lines = text.split('\n')
    header = lines[0]
    toc = "[TOC]\n"
    return '\n'.join([header, toc] + lines[1:])
