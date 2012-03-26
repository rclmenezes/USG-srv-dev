################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  globalsettings.py
# Info :  a few settings, with added individual ones
################################################################

from django.conf import settings
from datetime import datetime
#once again, the really important ones are one step deeper

#Sensitive info (passwords)
try:
    from local_settings import *
except ImportError, exp:
    print "Error: Couldn't import local_settings; missing passwords and other local data"

site_root = settings.CURRENT_DIR
our_site = 'http://%scal.tigerapps.org/' % settings.CURRENT_HOST_PREFIX
our_email = '%scal.tigerapps.org' % settings.CURRENT_HOST_PREFIX

cas_url = 'https://fed.princeton.edu/cas/'
our_site_validate = our_site + 'login'
SITE_ADMINS = ('usg','yaro','sshamim','nhantman','rmenezes')


dtdeleteflag = datetime(1900,1,1,0,0,0);

#Unused settings  (from SMTP mail)
EMAIL_HOST = 'mail.yahoo.com'
EMAIL_PORT = '25'
EMAIL_HOST_USER = 'princetoncalendar'
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = 'princetoncalendar@yahoo.com'
SERVER_EMAIL = 'princetoncalendar@yahoo.com'
SEND_BROKEN_LINK_EMAILS = True
EMAIL_USE_TLS = True
