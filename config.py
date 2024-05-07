
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

FRONTEND_SECRET_KEY = os.environ.get('FRONTEND_SECRET_KEY')
FRONTEND_HOST = os.environ.get('FRONTEND_HOST', '127.0.0.1')
FRONTEND_PORT = int(os.environ.get('FRONTEND_PORT', '8080'))

SCORE_RESPONSE_LIMIT = int(os.environ.get('SCORE_RESPONSE_LIMIT', 50))
DOMAIN_NAME = os.environ.get('DOMAIN_NAME')

APPROVED_MAP_REWARDS = eval(os.environ.get('APPROVED_MAP_REWARDS', 'False').capitalize())
ENABLE_SSL = eval(os.environ.get('ENABLE_SSL', 'False').capitalize())
S3_ENABLED = eval(os.environ.get('ENABLE_S3', 'True').capitalize())
DEBUG = eval(os.environ.get('DEBUG', 'False').capitalize())

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_EMAIL = os.environ.get('SENDGRID_EMAIL')

MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_EMAIL = os.environ.get('MAILGUN_EMAIL', '')
MAILGUN_URL = os.environ.get('MAILGUN_URL', 'api.eu.mailgun.net')
MAILGUN_DOMAIN = MAILGUN_EMAIL.split('@')[-1]

EMAILS_ENABLED = bool(MAILGUN_API_KEY or SENDGRID_API_KEY)
EMAIL = MAILGUN_EMAIL or SENDGRID_EMAIL

OFFICER_WEBHOOK_URL = os.environ.get('OFFICER_WEBHOOK_URL')
DATA_PATH = os.path.abspath('.data')