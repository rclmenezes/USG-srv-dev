import urllib
import urllib2
from django.contrib.auth.models import User
from django.conf import settings
from apps.students.models import RecentDepartments

cas_login_url = settings.CAS + '/login'
cas_logout_url = settings.CAS + '/logout'
cas_validate_url = settings.CAS + '/validate'
cas_scg_service_url = settings.CAS_SERVICE

class CASBackend:
    def authenticate(self, ticket=None):
        #validate
        html = urllib2.urlopen('%s?service=%s&ticket=%s' % (cas_validate_url,
                                                            cas_scg_service_url,
                                                            ticket)).read()
        validated, username, _ = html.split('\n')
        if validated == 'no':
            return None

        defaults = {'is_staff':False,
                    'is_active':True,
                    'is_superuser':False,
                    'email':str(username)+'@princeton.edu',
                    }
        user, _ = User.objects.get_or_create(username=username, defaults=defaults)
        r = RecentDepartments.objects
        user.recent_departments = r.recent_departments(user)
        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            r = RecentDepartments.objects
            user.recent_departments = r.recent_departments(user)
            return user
        except User.DoesNotExist:
            return None
