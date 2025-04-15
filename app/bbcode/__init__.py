
# Modified version of:
# https://github.com/dcwatson/bbcode/blob/master/bbcode.py

from .formatter import parser as formatter
from .regexes import _bbcode_url_re
from .objects import TagOptions
from .parser import Parser

import urllib.parse
import regex

def url_hotfix(input_text: str) -> str:
    """Fix the formatting of various URLs"""
    try:
        matches = _bbcode_url_re.finditer(input_text, timeout=0.2)
    except TimeoutError:
        return input_text

    for match in matches:
        url = match.group('url')
        unquoted_url = urllib.parse.unquote(url)

        input_text = input_text.replace(
            url,
            urllib.parse.quote(unquoted_url, safe=':/')
        )

    return input_text

def render_html(input_text, **context):
    """
    A module-level convenience method that creates a default bbcode parser,
    and renders the input string as HTML.
    """
    input_text = url_hotfix(input_text)
    return formatter.format(input_text, **context)
