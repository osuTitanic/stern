
# Modified version of:
# https://github.com/dcwatson/bbcode/blob/master/bbcode.py

from .formatter import parser as formatter
from .objects import TagOptions
from .parser import Parser

def render_html(input_text, **context):
    """
    A module-level convenience method that creates a default bbcode parser,
    and renders the input string as HTML.
    """
    return formatter.format(input_text, **context)
