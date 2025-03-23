
from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinksInlineProcessor
from app.wiki.constants import LINK_REGEX
from flask import request

class WikiLinks(WikiLinkExtension):
    def extendMarkdown(self, md):
        self.md = md
        WIKILINK_RE = LINK_REGEX.pattern
        wikilinkPattern = WikiLinksInlineProcessor(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)

    @staticmethod
    def buildUrl(label, base, end):
        return f'{base}{request.view_args.get("language", "")}/{label}{end}'

def makeExtension(**kwargs):
    return WikiLinks(**kwargs)
