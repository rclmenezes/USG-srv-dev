# Django settings for PTX project.
import os
from django.conf import settings


ROOT = os.path.dirname(__file__)


settings.STATIC_DOC_ROOT = '/srv/tigerapps/static/ptx/css'
settings.BOOK_CACHE_DIR = '/srv/tigerapps/media/ptx/book_cache'
#settings.DOCS_DIR = os.path.join(ROOT, 'ptx/docs/_build/html')
settings.APPEND_SLASH = False

settings.MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
    'ptx.middleware.ProcessPermDenied',
)

#settings.AUTHENTICATION_BACKENDS = (
#    'django.contrib.auth.backends.ModelBackend',
#    'ptx.ptxcasbackend.PopulatedCASBackend',
#)


#some weird logging shit
import socket
import logging
settings.log = logging.getLogger(__name__)
DEBUG = (socket.gethostname() != 'USG')
TEMPLATE_DEBUG = DEBUG
LOG = '[%(asctime)s %(name)s %(levelname)s] %(message)s'
if DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=LOG)
else:
    logging.basicConfig(level=logging.WARN,
                        format=LOG,
                        filename=os.path.join(ROOT, 'error.log'))
