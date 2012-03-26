import urllib
import urllib2
from django.contrib.auth.models import User
from django.conf import settings

hostname = 'http://%sttrade.tigerapps.org/' % settings.CURRENT_HOST_PREFIX
cas_login_url = settings.IAS + '/login'
cas_logout_url = settings.IAS + '/logout?url=' + urllib.quote(hostname, safe='')
cas_validate_url = settings.IAS + '/validate'
cas_ttrade_service_url = settings.IAS_SERVICE

class IASBackend:
    def authenticate(self, ticket=None):
        #validate
        html = urllib2.urlopen('%s?service=%s&ticket=%s' % (cas_validate_url,
                                                            cas_ttrade_service_url,
                                                            ticket)).read()
        result = html.split('\n')
        validated = result[0]
        username = result[1]
        if validated == 'no':
            return None

        defaults = {'is_staff':False,
                    'is_active':True,
                    'is_superuser':False,
                    'email':str(username)+'@ias.edu',
                    }
        sn = "ia_" + username
        user, _ = User.objects.get_or_create(username=sn, defaults=defaults)
        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None
