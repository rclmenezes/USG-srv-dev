import os
import sys
import socket

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

path = '/'.join(__file__.split('/')[:-2])
if path not in sys.path:
    sys.path.append(path)

if socket.gethostname() == 'USGDev':
    import imp
    import monitor
    monitor.start(interval=1.0)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
