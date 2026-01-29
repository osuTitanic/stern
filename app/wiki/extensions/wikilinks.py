
from app.wiki.constants import WIKI_LINK_REGEX
from markdown_it.common.utils import escapeHtml
from markdown_it.rules_inline import StateInline
from markdown_it import MarkdownIt
from contextlib import suppress
from flask import request

def wikilinks_plugin(
    md: MarkdownIt,
    base_url: str = '/wiki/',
    html_class: str = 'wikilink'
) -> None:
    """Plugin to handle [[wikilink]] and [[wikilink|label]] syntax"""

    def build_url(link: str) -> str:
        """Build url with language prefix from request"""
        language = ""

        # Suppress if outside request context
        with suppress(RuntimeError):
            language = request.view_args.get("language", "")

        if not language:
            return f'{base_url}{link}'

        return f'{base_url}{language}/{link}'

    def wikilink_def(state: StateInline, silent: bool) -> bool:
        """Parse wikilink inline rule"""
        if state.src[state.pos:state.pos + 2] != '[[':
            return False

        # Find the closing ]]
        match = WIKI_LINK_REGEX.match(state.src, state.pos)

        if not match:
            return False

        if not silent:
            link = match.group(1).strip()
            label = match.group(2).strip() if match.group(2) else link

            token = state.push('wikilink', 'a', 0)
            token.content = label
            token.meta = {'link': link}

        state.pos = match.end()
        return True

    def wikilink_render(self, tokens, idx, options, env) -> str:
        """Render wikilink token to HTML"""
        token = tokens[idx]
        link = token.meta['link']
        label = escapeHtml(token.content)
        url = build_url(link)
        return f'<a class="{html_class}" href="{url}">{label}</a>'

    md.inline.ruler.before('link', 'wikilink', wikilink_def)
    md.add_render_rule('wikilink', wikilink_render)
