from django.conf import settings
import re

class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        parts = request.domain.split('.')

        # xxx.tigerapps.org or xxx.localhost:8000
        if len(parts) == 4 or (re.match("^localhost", parts[-1]) and len(parts) == 2):
            request.subdomain = parts[1]
            request.domain = '.'.join(parts[1:])

        # set the right urlconf
        if request.subdomain == "":
            request.subdomain == 'index'
            
        settings.ROOT_URLCONF = request.subdomain + ".urls"

        ### INTRODUCING....
        ###
        ### A CONVULTED, HORRIBLE MESS
        ### TEMPORARY (I hope)
        if request.subdomain == 'ptx':
            import ptx.ptxsettings
            
        elif request.subdomain == 'ttrade':
            settings.AUTHENTICATION_BACKENDS = (
             'django.contrib.auth.backends.ModelBackend',
             'ttrade.casBackend.CASBackend',
             'ttrade.iasBackend.IASBackend',
            )
            
            # CAS URL.
            settings.CAS = 'https://fed.princeton.edu/cas'
            settings.CAS_SERVICE = 'http://dev.ttrade.tigerapps.org/cas/login/'
            settings.IAS = 'https://idp.ias.edu/cas'
            settings.IAS_SERVICE = 'http://dev.ttrade.tigerapps.org/ias/login/'    
            
        elif request.subdomain == 'cal':
            settings.MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'middleware.SubdomainsMiddleware',
            )
            settings.AUTHENTICATION_BACKENDS = (
                'django.contrib.auth.backends.ModelBackend',
            )
          
        else:
            settings.MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'middleware.SubdomainsMiddleware',
                'django_cas.middleware.CASMiddleware',
                'django.middleware.doc.XViewMiddleware',
            )
            settings.AUTHENTICATION_BACKENDS = (
                'django.contrib.auth.backends.ModelBackend',
                'django_cas.backends.CASBackend',
            )
            settings.CAS_SERVER_URL = 'https://fed.princeton.edu/cas/'
            settings.LOGIN_URL = '/login'
            settings.CAS_LOGOUT_COMPLETELY = True
            settings.CAS_IGNORE_REFERER = True
            settings.SITE_URL = 'http://dev.' + request.subdomain + '.tigerapps.org/'
            settings.CAS_REDIRECT_URL = settings.SITE_URL