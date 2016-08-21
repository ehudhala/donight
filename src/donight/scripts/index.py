from logging import getLogger

from donight.config.consts import DEBUG
from donight.event_finder.core import EventFinder

if __name__ == '__main__':
    logger = getLogger('donight.scripts.index')
    logger.info("Mode: {0}".format('Debug' if DEBUG else 'Production'))
    EventFinder().index_events()
