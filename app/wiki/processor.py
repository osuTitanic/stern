
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.deflist import deflist_plugin
from markdown_it import MarkdownIt
from app.wiki.extensions import *

md = MarkdownIt('commonmark', {'breaks': True, 'html': True, 'linkify': True}) \
    .use(front_matter_plugin) \
    .use(footnote_plugin) \
    .use(anchors_plugin, permalink=True, max_level=4, permalinkSymbol="") \
    .use(deflist_plugin) \
    .use(tasklists_plugin) \
    .use(highlight_code_plugin) \
    .use(wikilinks_plugin, base_url='/wiki/', html_class='wikilink') \
    .use(toc_plugin, marker='[TOC]', title='Contents') \
    .enable('table') \
    .enable('strikethrough') \
    .enable('linkify')

def process_markdown(text: str) -> str:
    """Process markdown text into HTML"""
    return md.render(text)
