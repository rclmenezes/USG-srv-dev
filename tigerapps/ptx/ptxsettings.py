# Django settings for PTX project.
import logging
from django.conf import settings
settings.log = logging.getLogger(__name__)

import os.path as paths

ROOT = paths.dirname(__file__)
DEBUG = True
TEMPLATE_DEBUG = False
settings.CAS = 'https://fed.princeton.edu/cas/'
LOG = '[%(asctime)s %(name)s %(levelname)s] %(message)s'

settings.STATIC_DOC_ROOT = '/srv/tigerapps/media/ptx/css'
settings.BOOK_CACHE_DIR = '/srv/tigerapps/media/ptx/book_cache'
settings.DOCS_DIR = paths.join(ROOT, 'ptx/docs/_build/html')

# List of callables that know how to import templates from various sources.
settings.TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

settings.MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ptx.middleware.ProcessPermDenied'
)


settings.APPEND_SLASH = False

if paths.exists(paths.join(ROOT, 'settingsdev.py')):
    from PTX.settingsdev import *

if DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=LOG)
else:
    logging.basicConfig(level=logging.WARN,
                        format=LOG,
                        filename=paths.join(ROOT, 'log'))
