import os
# Email/Database settings (sensitive info)
try:
    import local_settings
except ImportError, exp:
    print "Error: Couldn't import local_settings; missing passwords and other local data"


# CAS URL.
CAS = 'https://fed.princeton.edu/cas'
CAS_SERVICE = 'http://dev.scg.tigerapps.org/cas/login/'

CACHE_BACKEND = 'locmem:///'
CACHE_MIDDLEWARE_SECONDS = 60*5



#######################
#Stuff below should be taken out after eventual merge with tigerapps django project 
#######################

ABSPATH = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'scg',             # Or path to database file if using sqlite3.
        'USER': 'scg',             # Not used with sqlite3.
        'PASSWORD': local_settings.DATABASE_PASSWORD,
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
# Make this unique, and don't share it with anybody.
SECRET_KEY = local_settings.SECRET_KEY


# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(ABSPATH, 'media/')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#TODO: doesn't work since django.contrib.staticfiles added
ADMIN_MEDIA_PREFIX = '/admin_media/'

#STATIC_ROOT = CURRENT_DIR + "/media" #TODO: this doesn't work
STATIC_URL = "/media"
STATICFILES_DIRS = (
    ABSPATH + "/media",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ABSPATH, 'templates/'),
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
    'django.middleware.doc.XViewMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'backends.ldapBackend.LDAPBackend',
    'backends.casBackend.CASBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    'django.core.context_processors.request',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'apps.professors',
    'apps.courses',
    'apps.students',
    'apps.reviews',
    'apps.elearn',
)

ROOT_URLCONF = 'urls'

DATABASE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'

