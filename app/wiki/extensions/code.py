
from pygments.lexers import get_lexer_by_name, guess_lexer, ClassNotFound
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments import highlight

from markdown_it.common.utils import escapeHtml
from markdown_it import MarkdownIt
from contextlib import suppress

def highlight_code_plugin(md: MarkdownIt) -> None:
    """Plugin to add syntax highlighting to fenced code blocks"""

    def render_fence(self, tokens, idx, options, env) -> str:
        """Custom fence renderer with Pygments highlighting"""
        token = tokens[idx]
        info = token.info.strip() if token.info else ''

        lang = info.split()[0] if info else ''
        code = token.content
        lexer = resolve_lexer(lang, code)

        if lexer:
            formatter = HtmlFormatter(cssclass='codehilite', wrapcode=True)
            return highlight(code, lexer, formatter)

        # Fallback to default rendering
        escaped = escapeHtml(code)
        lang_class = f' class="language-{escapeHtml(lang)}"' if lang else ''
        return f'<pre><code{lang_class}>{escaped}</code></pre>\n'

    def resolve_lexer(lang: str, code: str) -> 'Lexer | None':
        """Resolve the appropriate Pygments lexer for the given language"""
        with suppress(ClassNotFound):
            return (
                get_lexer_by_name(lang, stripall=True) if lang else
                guess_lexer(code)
            )

        return None

    md.add_render_rule('fence', render_fence)
