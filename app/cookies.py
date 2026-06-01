from app.common.config import config_instance as config
from app.common.helpers import browsers

from flask.sessions import SecureCookieSessionInterface
from flask import has_request_context, request

class FrontendSessionInterface(SecureCookieSessionInterface):
    """Custom session interface for consistent cookie attributes"""
    def get_cookie_secure(self, app) -> bool:
        return determine_secure()

    def get_cookie_samesite(self, app) -> str | None:
        return determine_samesite()

def determine_samesite(user_agent: str | None = None) -> str | None:
    """Determine the 'SameSite' attribute for cookies based on the user agent"""
    if should_omit_samesite(user_agent):
        return None

    return "Lax"

def determine_secure() -> bool:
    """Determine whether to set the 'Secure' attribute for cookies"""
    if not config.ENABLE_SSL:
        return False

    if not config.ALLOW_INSECURE_COOKIES:
        return True

    if not has_request_context():
        return False

    return request.is_secure

def should_omit_samesite(user_agent: str | None = None) -> bool:
    user_agent = user_agent or flask_request_user_agent()
    return not browsers.is_modern_browser(user_agent)

def flask_request_user_agent() -> str:
    if not has_request_context():
        return ""

    return request.user_agent.string or ""
