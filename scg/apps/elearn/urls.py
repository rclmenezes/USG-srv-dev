from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^scg/', include('apps.foo.urls.foo')),

    # Uncomment this for admin:
     (r'^post/$', 'apps.elearn.views.post'),
)
