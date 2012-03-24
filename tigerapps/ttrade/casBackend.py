import urllib
from django_cas.urllib2_sslv3 import urllib2
from django.contrib.auth.models import User
from django.conf import settings

cas_login_url = settings.CAS + '/login'
cas_logout_url = settings.CAS + '/logout?url=http%3A%2F%2Fdev.ttrade.tigerapps.org%2F'
cas_validate_url = settings.CAS + '/validate'
cas_ttrade_service_url = settings.CAS_SERVICE

class CASBackend:
    def authenticate(self, ticket=None):
        #validate
        html = urllib2.urlopen('%s?service=%s&ticket=%s' % (cas_validate_url,
                                                            cas_ttrade_service_url,
                                                            ticket)).read()
        validated, username, _ = html.split('\n')
        if validated == 'no':
            return None

        defaults = {'is_staff':False,
                    'is_active':True,
                    'is_superuser':False,
                    'email':str(username)+'@princeton.edu',
                    }
        sn = "pr_" + username
        user, _ = User.objects.get_or_create(username=sn, defaults=defaults)
        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None
