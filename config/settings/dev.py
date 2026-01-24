from dotenv import load_dotenv
from .base import *  # noqa

load_dotenv()  # For .env file support

DEBUG = True

# local defaults
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
