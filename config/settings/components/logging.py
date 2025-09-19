"""
Logging configuration.
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
