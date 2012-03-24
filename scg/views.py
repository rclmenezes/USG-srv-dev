import urllib,urllib2

from django.contrib.auth import logout, authenticate, login
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from apps.courses.models import Offering, Course, CrossList, THIS_YEAR, THIS_SEMESTER, NEXT_SEMESTER, NEXT_YEAR
from apps.students.models import RecentCourses, RecentDepartments, MyCourse
from apps.reviews.models import CourseReview, ProfessorReview
from backends import casBackend

def login_view_redirect(request):
    if request.GET.get('key', None) == None:
        return HttpResponseRedirect('http://scg.tigerapps.org/accounts/login/secure/?next=%s' % request.GET.get('next','/'))
    else:
        #auth stuff here
        pass

def login_view(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('http://scg.tigerapps.org/%s' % request.GET.get('next','/'))
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass


    return render_to_response('login.html')

def cas_login(request):
    ticket = request.GET.get('ticket', None)
    if ticket is None:
        return HttpResponseRedirect('%s?service=%s' %
                                            (casBackend.cas_login_url,
                                             casBackend.cas_scg_service_url))
    else:
        #validate
        user = authenticate(ticket=ticket)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('/')
            else:
                #return inactive page
                pass
        else:
            #return user does not exist
            pass
    return HttpResponseRedirect(casBackend.cas_scg_service_url)

def cas_logout(request):
    logout(request)
    return HttpResponseRedirect(casBackend.cas_logout_url)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def index(request):
    recent_courses = RecentCourses.objects.recent_courses(request.user, 10)

    #cache popular_courses for speed
    popular_courses = cache.get('popular_courses')
    if not popular_courses:
        popular_courses = RecentCourses.objects.popular_courses()
        cache.set('popular_courses', popular_courses, 60 * 60)

    this_year = \
        Q(offering__year__exact=THIS_YEAR) & Q(offering__semester__exact=THIS_SEMESTER)
    next_year = \
        Q(offering__year__exact=NEXT_YEAR) & Q(offering__semester__exact=NEXT_SEMESTER)
    mycourses = MyCourse.objects.filter(this_year | next_year,
                                        user=request.user)

    data = {'recent_courses': recent_courses,
            'popular_courses': popular_courses,
            'mycourses': mycourses,
            'NEXT_SEMESTER': NEXT_SEMESTER,
            'NEXT_YEAR': NEXT_YEAR,
            'THIS_SEMESTER': THIS_SEMESTER,
            'THIS_YEAR': THIS_YEAR,
            }

    return render_to_response('index.html',
                              data,
                              context_instance=RequestContext(request))


