
import dotenv
import os

dotenv.load_dotenv(override=True)

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')

POSTGRES_POOLSIZE = int(os.environ.get('POSTGRES_POOLSIZE', 10))
POSTGRES_POOLSIZE_OVERFLOW = int(os.environ.get('POSTGRES_POOLSIZE_OVERFLOW', 30))

S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_BASEURL    = os.environ.get('S3_BASEURL')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

FRONTEND_HOST = os.environ.get('FRONTEND_HOST', '127.0.0.1')
FRONTEND_PORT = int(os.environ.get('FRONTEND_PORT', '8080'))
FRONTEND_SECRET_KEY = os.environ.get('FRONTEND_SECRET_KEY')
FRONTEND_TOKEN_EXPIRY = int(os.environ.get('FRONTEND_TOKEN_EXPIRY', 3600))
FRONTEND_REFRESH_EXPIRY = int(os.environ.get('FRONTEND_REFRESH_EXPIRY', 3600*24*30))

SCORE_RESPONSE_LIMIT = int(os.environ.get('SCORE_RESPONSE_LIMIT', 50))
DOMAIN_NAME = os.environ.get('DOMAIN_NAME')

DEBUG = eval(os.environ.get('DEBUG', 'False').capitalize())
S3_ENABLED = eval(os.environ.get('ENABLE_S3', 'True').capitalize())
ENABLE_SSL = eval(os.environ.get('ENABLE_SSL', 'False').capitalize())
APPROVED_MAP_REWARDS = eval(os.environ.get('APPROVED_MAP_REWARDS', 'False').capitalize())
ALLOW_INSECURE_COOKIES = eval(os.environ.get('ALLOW_INSECURE_COOKIES', 'False').capitalize()) or DEBUG

EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_DOMAIN = EMAIL_SENDER.split('@')[-1]

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT') or '587')
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_URL = os.environ.get('MAILGUN_URL', 'api.eu.mailgun.net')

EMAILS_ENABLED = bool(EMAIL_PROVIDER and EMAIL_SENDER)

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')

OFFICER_WEBHOOK_URL = os.environ.get('OFFICER_WEBHOOK_URL')
EVENT_WEBHOOK_URL = os.environ.get('EVENT_WEBHOOK_URL')
DATA_PATH = os.path.abspath('.data')

WIKI_REPOSITORY_OWNER = os.environ.get('WIKI_REPOSITORY_OWNER', 'osuTitanic')
WIKI_REPOSITORY_NAME = os.environ.get('WIKI_REPOSITORY_NAME', 'wiki')
WIKI_REPOSITORY_BRANCH = os.environ.get('WIKI_REPOSITORY_BRANCH', 'main')
WIKI_REPOSITORY_PATH = os.environ.get('WIKI_REPOSITORY_PATH', 'wiki')
WIKI_DEFAULT_LANGUAGE = os.environ.get('WIKI_DEFAULT_LANGUAGE', 'en')

DEFAULT_API_BASEURL = f'http{"s" if ENABLE_SSL else ""}://api.{DOMAIN_NAME}'
DEFAULT_OSU_BASEURL = f'http{"s" if ENABLE_SSL else ""}://osu.{DOMAIN_NAME}'
DEFAULT_STATIC_BASEURL = f'http{"s" if ENABLE_SSL else ""}://s.{DOMAIN_NAME}'

API_BASEURL = os.environ.get('API_BASEURL', DEFAULT_API_BASEURL)
OSU_BASEURL = os.environ.get('OSU_BASEURL', DEFAULT_OSU_BASEURL)
STATIC_BASEURL = os.environ.get('STATIC_BASEURL', DEFAULT_STATIC_BASEURL)