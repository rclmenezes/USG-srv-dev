#!/usr/bin/python
# This script runs the real-time server instance

from gevent.pywsgi import WSGIServer
import os, sys, time
sys.path.append('/home/jgiles/USG-srv-dev')
os.environ['DJANGO_SETTINGS_MODULE'] = 'tigerapps.settings'
os.environ['IS_REAL_TIME_SERVER'] = 'TRUE'

import django.core.handlers.wsgi

import os, subprocess
PIDFILE = '/srv/eggs/rooms_server_pid'
pid = os.getpid()

PORT = 8131


def log(mess):
    f = open('/home/jgiles/out.log', 'a')
    f.write(mess + '\n')
    f.close()

#log('Serverscript has been invoked')

# Kill the old server if need be
if os.path.exists(PIDFILE):
    f = open(PIDFILE)
    #log('Going to kill old server')
    oldpid = int(f.read())
    #subprocess.call('kill -15 %d' % oldpid, shell=True)
    code = subprocess.call(['kill', '-15', str(oldpid)])
    #print code
    f.close()

# Write the new pid
f = open(PIDFILE, 'w')
f.write(str(pid))
f.close()

application = django.core.handlers.wsgi.WSGIHandler()

TRIES = 5
if __name__ == '__main__':
    print 'Real-time server on %d...' % PORT
    for i in range(0, TRIES):
        try:
            WSGIServer(('', PORT), application).serve_forever()
        except:
            time.sleep(.01)
    print 'Real-time server not running'
