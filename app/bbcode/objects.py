
from collections.abc import Mapping, MutableMapping
from collections import OrderedDict

# Taken from https://github.com/psf/requests/blob/eedd67462819f8dbf8c1c32e77f9070606605231/requests/structures.py#L15
class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))

class TagOptions:
    # The name of the tag, all lowercase.
    tag_name = None

    # True if a newline should automatically close this tag.
    newline_closes = False

    # True if another start of the same tag should automatically close this tag.
    same_tag_closes = False

    # True if this tag does not have a closing tag.
    standalone = False

    # True if tags should be rendered inside this tag.
    render_embedded = True

    # True if newlines should be converted to markup.
    transform_newlines = True

    # True if HTML characters (<, >, and &) should be escaped inside this tag.
    escape_html = True

    # True if URLs should be replaced with link markup inside this tag.
    replace_links = True

    # True if cosmetic replacements (elipses, dashes, etc.) should be performed inside this tag.
    replace_cosmetic = True

    # True if leading and trailing whitespace should be stripped inside this tag.
    strip = False

    # True if this tag should swallow the first trailing newline (i.e. for block elements).
    swallow_trailing_newline = False

    def __init__(self, tag_name, **kwargs):
        self.tag_name = tag_name
        for attr, value in list(kwargs.items()):
            setattr(self, attr, bool(value))
