import os

from donight.utils import SECONDS_IN_DAY

DEBUG = True

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

if not DEBUG:
    # Real DB configuration. (Should only be used in production)
    DB_ENGINE = ''
    DB_ADDRESS = ''
    DB_NAME = ''
    DB_USERNAME = ''
    DB_PASSWORD = ''
    DB_CONNECTION_STRING = '{0}://{1}:{2}@{3}/{4}'.format(
        DB_ENGINE, DB_USERNAME, DB_PASSWORD, DB_ADDRESS, DB_NAME)
else:
    DB_PATH = os.path.join(ROOT_DIR, 'db.sqlite3')
    DB_CONNECTION_STRING = 'sqlite:///{0}'.format(DB_PATH)

LOG_PATH = os.path.join(ROOT_DIR, 'log.txt')
SCRAPERS_LOG_PATH = os.path.join(ROOT_DIR, 'scrapers_log.txt')
EXTERNALS_LOG_PATH = os.path.join(ROOT_DIR, 'externals_log.txt')

TIME_BETWEEN_INDEXES = SECONDS_IN_DAY / 4

