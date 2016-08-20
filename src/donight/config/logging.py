from donight.config.consts import SCRAPERS_LOG_PATH, LOG_PATH, EXTERNALS_LOG_PATH

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s:%(name)s (%(asctime)s): %(message)s '
                      '(%(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH,
            'encoding': 'utf8',
            'maxBytes': 100000,
            'backupCount': 1,
        },
        'scrapers_file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SCRAPERS_LOG_PATH,
            'encoding': 'utf8',
            'maxBytes': 100000,
            'backupCount': 1,
        },
        # 'externals_file': {
        #     'level': 'DEBUG',
        #     'formatter': 'standard',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': EXTERNALS_LOG_PATH,
        #     'encoding': 'utf8',
        #     'maxBytes': 100000,
        #     'backupCount': 1,
        # }
    },
    'loggers': {
        'donight': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'donight.event_finder.scrapers': {
            'handlers': ['console', 'scrapers_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        # '': {
        #     'handlers': ['externals_file'],
        #     'level': 'DEBUG',
        # },
    }
}
