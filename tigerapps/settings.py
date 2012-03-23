# Django settings for tigerapps project.
import os, sys, socket
# Email/Database settings (sensitive info)
try:
    import local_settings
except ImportError, exp:
    print "Error: Couldn't import local_settings; missing passwords and other local data"



DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('USG IT', 'it@princetonusg.com'),
)
MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tigerapps',             # Or path to database file if using sqlite3.
        'USER': 'tigerapps',             # Not used with sqlite3.
        'PASSWORD': local_settings.DATABASE_PASSWORD,
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}


#os.environ['PYTHON_EGG_CACHE'] = '/srv/tigerapps/eggs' 
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_HOST = socket.gethostname()

SITE_ID = 1
# Make this unique, and don't share it with anybody.
SECRET_KEY = local_settings.SECRET_KEY



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False



# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = CURRENT_DIR + "/media/"
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#TODO: doesn't work since django.contrib.staticfiles added
ADMIN_MEDIA_PREFIX = '/admin_media/'

#STATIC_ROOT = CURRENT_DIR + "/media" #TODO: this doesn't work
STATIC_URL = "/media"
STATICFILES_DIRS = (
    CURRENT_DIR + "/media",
)



# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.csrf.CsrfViewMiddleware',
    'middleware.SubdomainsMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    CURRENT_DIR + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'cal',
    'dvd',
    'ptx',
    'my',
    'myapps',
    'groups',
    'ttrade',
    'card',
    'ccc',
    'elections',
    'facebook',
    'album',
    'pam'
)
