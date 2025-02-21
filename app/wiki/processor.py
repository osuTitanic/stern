
import markdown

MARKDOWN = markdown.Markdown(
    extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
    ]
)

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return MARKDOWN.convert(text)
