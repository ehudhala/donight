import os

from donight.utils import SECONDS_IN_DAY

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

DB_PATH = os.path.join(ROOT_DIR, 'db.sqlite3')

LOG_PATH = os.path.join(ROOT_DIR, 'log.txt')
SCRAPERS_LOG_PATH = os.path.join(ROOT_DIR, 'scrapers_log.txt')
EXTERNALS_LOG_PATH = os.path.join(ROOT_DIR, 'externals_log.txt')

TIME_BETWEEN_INDEXES = SECONDS_IN_DAY / 4

