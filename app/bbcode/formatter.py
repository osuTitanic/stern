
from urllib.parse import unquote, urlparse
from app.common.constants import regexes
from .parser import Parser

import binascii
import hashlib
import config
import hmac

parser = Parser()
parser.add_simple_formatter('b', '<b>%(value)s</b>')
parser.add_simple_formatter('i', '<i>%(value)s</i>')
parser.add_simple_formatter('u', '<u>%(value)s</u>')
parser.add_simple_formatter('heading', '<h2>%(value)s</h2>')
parser.add_simple_formatter('strike', '<strike>%(value)s</strike>')
parser.add_simple_formatter('centre', '<center>%(value)s</center>')

parser.add_simple_formatter(
    'code',
    '%(value)s',
    same_tag_closes=True,
    render_embedded=False,
    transform_newlines=True,
    escape_html=True,
    replace_links=False
)

parser.add_simple_formatter(
    'c',
    '%(value)s',
    same_tag_closes=True,
    render_embedded=False,
    transform_newlines=True,
    escape_html=True,
    replace_links=False
)

parser.add_simple_formatter(
    '*',
    '<li>%(value)s</li>',
    same_tag_closes=True
)

parser.add_simple_formatter(
    'spoilerbox',
    '<div class="spoiler">'
    '<div class="spoiler-head" onclick="return toggleSpoiler(this);">SPOILER</div>'
    '<div class="spoiler-body">%(value)s</div>'
    '</div>'
)

@parser.formatter('img', replace_links=False, render_embedded=False)
def render_image(tag_name, value, options, parent, context):
    if not (url := resolve_proxied_url(value)):
        return ''

    return '<img src="%s" loading="lazy">' % sanitize_input(url)

@parser.formatter('video', replace_links=False, render_embedded=False)
def render_video(tag_name, value, options, parent, context):
    if not (url := resolve_proxied_url(value)):
        return ''

    return '<video src="%s" controls></video>' % sanitize_input(url)

@parser.formatter('box')
def render_box(tag_name, value, options, parent, context):
    return '<div class="spoiler">' \
           '<div class="spoiler-head" onclick="return toggleSpoiler(this);">%s</div>' \
           '<div class="spoiler-body">%s</div>' \
           '</div>' % (sanitize_input(options.get('box', '')), value)

@parser.formatter('color')
def render_color(tag_name, value, options, parent, context):
    color = sanitize_input(options.get('color', '')).replace(";", "")
    return '<span style="color:%s;">%s</span>' % (color, value)

@parser.formatter('profile')
def render_profile(tag_name, value, options, parent, context):
    profile = sanitize_input(options.get('profile', value))
    return '<a href="%s/u/%s">%s</a>' % (config.OSU_BASEURL, profile, value)

@parser.formatter('youtube', render_embedded=False, replace_links=False)
def render_youtube_embed(tag_name, value, options, parent, context):
    # Filter out video ID
    value = (
        value.split('/')[-1]
        if '/' in value else value
    )

    # Remove watch?v=
    value = value.replace('watch?v=', '')

    return (
        '<iframe width="373" height="210" src="https://www.youtube.com/embed/%s"'
        'title="YouTube Video Player" frameborder="0" allow="accelerometer; autoplay;'
        'clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"'
        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>' % value
    )

@parser.formatter('google', render_embedded=False)
def render_google(tag_name, value, options, parent, context):
    return '<a href="https://letmegooglethat.com/?q=%s" target="_blank">%s</a>' % (value, value)

@parser.formatter('url')
def render_link(tag_name, value, options, parent, context):
    url = sanitize_url(unquote(options.get('url', '')))
    return '<a href="%s" target="_blank">%s</a>' % (url, value)

@parser.formatter('quote')
def render_quote(tag_name, value, options, parent, context):
    if 'quote' not in options:
        return '<blockquote>%s</blockquote>' % value

    return (
        '<blockquote>'
        '<h4>%s wrote:</h4><i>'
        '%s'
        '</i></blockquote>' % (options["quote"], value)
    )

@parser.formatter('size')
def render_size(tag_name, value, options, parent, context):
    size = options.get('size', '100')

    if size.isdigit():
        size = max(10, min(800, int(size)))
        return '<span style="font-size:%s%%;">%s</span>' % (size, value)

    size_strings = {
        'tiny': 50,
        'small': 85,
        'normal': 100,
        'large': 180
    }

    if size not in size_strings:
        return value

    return '<span style="font-size:%s%%;">%s</span>' % (size_strings[size], value)

@parser.formatter('list')
def render_list(tag_name, value, options, parent, context):
    if 'list' in options:
        return '<ol>%s</ol>' % value

    return '<ul>%s</ul>' % value

@parser.formatter('email', render_embedded=False)
def render_email(tag_name, value, options, parent, context):
    email = sanitize_input(
        options.get('email')
        if 'email' in options
        else value
    )

    if not (regexes.EMAIL.match(email)):
        return value

    return '<a href="mailto:%s">%s</a>' % (email, value)

def sanitize_input(text: str) -> str:
    for sequence, replace in Parser.REPLACE_ESCAPE:
        text = text.replace(sequence, replace)

    return text

def sanitize_url(text: str) -> str:
    text = sanitize_input(text)

    if not text.startswith('http'):
        text = 'http://' + text

    return text

def resolve_proxied_url(value) -> str:
    if not value:
        return ''

    # Try to parse URL
    parsed_url = urlparse(value)

    if not parsed_url.scheme or not parsed_url.netloc:
        return ''
    
    if not config.IMAGE_PROXY_BASEURL:
        # No image proxy configured, return original URL
        return value

    domain = parsed_url.netloc.lower().split(':')[0]

    if domain not in config.VALID_IMAGE_SERVICES:
        # Use image proxy for non-trusted domains
        signed_url = sign_url(value, config.FRONTEND_SECRET_KEY.encode())
        value = config.IMAGE_PROXY_BASEURL + signed_url

    return value

def sign_url(url: str, key: bytes) -> str:
    # Compute HMAC‑SHA1 for URL
    url_bytes = url.encode('utf-8')
    mac = hmac.new(key, url_bytes, hashlib.sha1).digest()

    # Hex‑encode the computed MAC & URL
    mac_hex = binascii.hexlify(mac).decode('ascii')
    url_hex = binascii.hexlify(url_bytes).decode('ascii')

    # Return the signed path
    return f"/{mac_hex}/{url_hex}"
