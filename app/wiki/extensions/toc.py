
from markdown_it.rules_inline import StateInline
from markdown_it.common.utils import escapeHtml
from markdown_it import MarkdownIt
from typing import Iterator
import re

def toc_plugin(
    md: MarkdownIt,
    marker: str = "[TOC]",
    title: str = "Contents",
    min_level: int = 1,
    max_level: int = 4
) -> None:
    """Plugin to generate table of contents from headings"""

    def collect_headings(state: StateInline) -> Iterator[dict]:
        """Returns an iterator of all headings for TOC generation"""
        for i, token in enumerate(state.tokens):
            if token.type != "heading_open":
                continue

            if i + 1 >= len(state.tokens):
                continue

            inline_token = state.tokens[i + 1]
            if inline_token.type != "inline":
                continue

            level = int(token.tag[1])
            text = inline_token.content
            slug = re.sub(r"[^\w\s-]", "", text.lower())
            slug = re.sub(r"[\s_]+", "-", slug).strip("-")

            if level < min_level or level > max_level:
                # Skip headings outside the specified level range
                continue

            yield {
                "level": level,
                "text": text,
                "slug": slug
            }

    def render_toc(toc_items: list) -> str:
        """Render the table of contents HTML"""
        # Filter out the first h1, i.e. the article title
        if toc_items and toc_items[0]["level"] == 1:
            toc_items = toc_items[1:]

        if not toc_items:
            return ""

        parts = [f'<div class="toc"><span class="toctitle">{title}</span><ul>']
        prev_level = toc_items[0]["level"]
        first = True

        for item in toc_items:
            level_diff = item["level"] - prev_level

            if level_diff > 0:
                parts.append("<ul>" * level_diff)
            elif level_diff < 0:
                parts.append("</li></ul>" * (-level_diff) + "</li>")
            elif not first:
                parts.append("</li>")

            parts.append(f'<li><a href="#{item["slug"]}">{escapeHtml(item["text"])}</a>')
            prev_level = item["level"]
            first = False

        # Close remaining tags
        depth = prev_level - toc_items[0]["level"] + 1
        parts.append("</li>" + "</ul>" * depth + "</div>")
        return "".join(parts)

    def replace_toc_marker(state: StateInline) -> None:
        """Replace [TOC] marker with generated TOC"""
        toc_items = list(collect_headings(state))
        index = 0

        while index < len(state.tokens):
            token = state.tokens[index]

            if not (token.type == "inline" and token.content and token.content.strip() == marker):
                # Not a TOC marker, continue
                index += 1
                continue

            if index == 0 or state.tokens[index - 1].type != "paragraph_open":
                # TOC marker not inside a paragraph, skip
                index += 1
                continue

            # Replace paragraph_open with html_block containing TOC
            html_token = state.tokens[index - 1]
            html_token.type = "html_block"
            html_token.tag = ""
            html_token.nesting = 0
            html_token.content = render_toc(toc_items)

            # Remove inline and paragraph_close tokens
            end = index + 1

            if end < len(state.tokens) and state.tokens[end].type == "paragraph_close":
                # Also remove paragraph_close token
                end += 1

            del state.tokens[index:end]

    md.core.ruler.push("toc", replace_toc_marker)
