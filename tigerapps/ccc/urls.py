from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()
handler404 = 'ccc.views.view_404'

urlpatterns = patterns('',
    (r'^/?$', 'ccc.views.index'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    
    url(r'^blog/?$', 'ccc.views.blog'),
    url(r'^log/?$', 'ccc.views.log_hours'),
    url(r'^request/?$', 'ccc.views.project_request'),
    url(r'^leaderboard/?$', 'ccc.views.leaderboard'),
    url(r'^hours_admin/?$', 'ccc.views.hours_admin'),
    url(r'^hours_admin/get_user_hours/?$', 'ccc.views.get_user_hours'),
    url(r'^hours_admin/get_month_group_hours/?$', 'ccc.views.get_month_group_hours'),
    url(r'^hours_admin/get_user_awards/?$', 'ccc.views.get_user_awards'),
    url(r'^hours_admin/post_user_awards/?$', 'ccc.views.post_user_awards'),
    
    #not sure if these work
    url(r'^all_hours/?$', 'ccc.views.all_hours'),
    url(r'^top/?$', 'ccc.views.top'),
    
    #blog posts
    #url(r'^log-test/?$', 'ccc.views.log_choices'),
    #url(r'^logging/?$', 'ccc.views.post', kwargs={'postTitle': "Logging"}),
    #url(r'^contact/?$', 'ccc.views.post', kwargs={'postTitle': "Contact Us"}),
    url(r'^about/?$', 'ccc.views.post', kwargs={'postTitle': "About"}),
    url(r'^opportunities/?$', 'ccc.views.post', kwargs={'postTitle': "Find an Opportunity!"}),
    url(r'^thankyou/?$', 'ccc.views.post', kwargs={'postTitle': "\"Thank You\"s"}),
    
    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
        
    # Try to find a post called that (must be last)
    url(r'^(?P<postTitle>\w+)/?$', 'ccc.views.post'),
)

urlpatterns += staticfiles_urlpatterns()

