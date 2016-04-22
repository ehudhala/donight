import os

from donight.utils import SECONDS_IN_DAY

DB_NAME = 'db.sqlite3'
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

TIME_BETWEEN_INDEXES = SECONDS_IN_DAY / 4

