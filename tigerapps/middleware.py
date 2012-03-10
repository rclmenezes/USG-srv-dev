from django.conf import settings
<<<<<<< HEAD
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
=======

class SubdomainsMiddleware:
    def process_request(self, request):
        #Find the subdomain
        request.domain = request.META['HTTP_HOST']
        parts = request.domain.split('.')

        if parts[0] == "dev":
            if len(parts) == 4:
                # dev.___.tigerapps.org
                request.subdomain = parts[1]
                request.domain = '.'.join(parts[2:])
            elif len(parts) == 3:
                # dev.tigerapps.org
                request.subdomain == 'www'
        else:
            if len(parts) == 3:
                # ___.tigerapps.org
                request.subdomain = parts[0]
                request.domain = '.'.join(parts[1:])
            else:
                request.subdomain == 'www'


        # set the right urlconf
        request.urlconf = request.subdomain + ".urls"

>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457

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
<<<<<<< HEAD
            settings.CAS_REDIRECT_URL = settings.SITE_URL
=======
            settings.CAS_REDIRECT_URL = settings.SITE_URL
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
