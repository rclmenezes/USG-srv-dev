from django.conf import settings

class SubdomainsMiddleware:
    def process_request(self, request):
        #Find the subdomain
        request.domain = request.META['HTTP_HOST']
        parts = request.domain.split('.')

        if parts[0] == "dev":
            url_prefix = "http://dev."
            if len(parts) == 4:
                # dev.___.tigerapps.org
                request.subdomain = parts[1]
                request.domain = '.'.join(parts[2:])
            else:
                # dev.tigerapps.org
                request.subdomain = 'www'
        else:
            url_prefix = "http://"
            if len(parts) == 3 and parts[0] != 'www':
                # ___.tigerapps.org
                request.subdomain = parts[0]
                request.domain = '.'.join(parts[1:])
            else:
                request.subdomain = 'www'
        settings.SITE_DOMAIN = url_prefix+request.domain

        # set the right urlconf
        if request.subdomain != 'www':
            request.urlconf = request.subdomain + ".urls"
        


        ### INTRODUCING....
        ###
        ### A CONVULTED, HORRIBLE MESS
        ### TEMPORARY (I hope)
        if request.subdomain == 'ttrade':
            settings.AUTHENTICATION_BACKENDS += (
                'ttrade.casBackend.CASBackend',
                'ttrade.iasBackend.IASBackend',
            )
            
            # CAS URL.
            settings.CAS = 'https://fed.princeton.edu/cas'
            settings.CAS_SERVICE = url_prefix + 'ttrade.tigerapps.org/cas/login/'
            settings.IAS = 'https://idp.ias.edu/cas'
            settings.IAS_SERVICE = url_prefix + 'ttrade.tigerapps.org/ias/login/'    
            
        elif request.subdomain == 'cal':
            #Nothing different from default; no auth backend (weird)
            pass
          
        else:
            settings.MIDDLEWARE_CLASSES += (
                'django_cas.middleware.CASMiddleware',
                'django.middleware.doc.XViewMiddleware',
            )
            settings.AUTHENTICATION_BACKENDS += (
                'django_cas.backends.CASBackend',
            )
            settings.CAS_SERVER_URL = 'https://fed.princeton.edu/cas/'
            settings.LOGIN_URL = '/login'
            settings.CAS_LOGOUT_COMPLETELY = True
            settings.CAS_IGNORE_REFERER = True
            settings.CAS_RETRY_LOGIN = True
            settings.SITE_URL = url_prefix + request.subdomain + '.tigerapps.org/'
            settings.CAS_REDIRECT_URL = settings.SITE_URL

            if request.subdomain == 'ptx':
                import ptx.ptxsettings


