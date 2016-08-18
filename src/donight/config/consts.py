import os

from donight.utils import SECONDS_IN_DAY

DEBUG = True

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

if DEBUG:
    DB_PATH = os.path.join(ROOT_DIR, 'db.sqlite3')
    DB_CONNECTION_STRING = 'sqlite:///{0}'.format(DB_PATH)
else:
    # PostgreSQL configuration. (Should only be used in production)
    DB_ADDRESS = None
    DB_NAME = None
    DB_USERNAME = None
    DB_PASSWORD = None
    DB_CONNECTION_STRING = 'postgresql://{0}:{1}@{2}/{3}'.format(
        DB_USERNAME, DB_PASSWORD, DB_ADDRESS, DB_NAME)

LOG_PATH = os.path.join(ROOT_DIR, 'log.txt')
SCRAPERS_LOG_PATH = os.path.join(ROOT_DIR, 'scrapers_log.txt')
EXTERNALS_LOG_PATH = os.path.join(ROOT_DIR, 'externals_log.txt')

TIME_BETWEEN_INDEXES = SECONDS_IN_DAY / 4

