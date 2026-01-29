
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.deflist import deflist_plugin
from markdown_it import MarkdownIt

md = MarkdownIt('commonmark', {'breaks': True, 'html': True}) \
    .use(front_matter_plugin) \
    .use(footnote_plugin) \
    .use(anchors_plugin, permalink=True, max_level=4, permalinkSymbol="") \
    .use(deflist_plugin) \
    .use(tasklists_plugin) \
    .enable('table') \
    .enable('strikethrough')

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return md.render(text)
