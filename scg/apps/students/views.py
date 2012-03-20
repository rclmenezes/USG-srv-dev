from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User

from apps.courses.models import THIS_YEAR, THIS_SEMESTER, NEXT_SEMESTER, NEXT_YEAR, Offering, Section
from apps.students.models import MyCourse, MySection

def class_roster(request, cid):
    try:
        o = Offering.objects.get(semester=THIS_SEMESTER, year=THIS_YEAR, course__cid=cid)
        students = User.objects.filter(mycourse__offering=o)
    except:
        students = None

    return render_to_response('students/class_roster.html', {'students':students,}, context_instance = RequestContext(request))

@login_required
def add_mycourse(request, cid, semester, year):
    try:
        offering = Offering.objects.get(course=int(cid), semester=semester, year=year)
    except:
        return HttpResponse('Hey!  This course is not offered in '+ semester + year +'!')
    MyCourse.objects.get_or_create(user=request.user, offering=offering)
    return HttpResponseRedirect('/')

@login_required
def add_mysection(request, sid):
    try:
        section = Section.objects.get(sid=str(sid))
        mycourse = MyCourse.objects.get(user=request.user, offering__section=section)
    except:
        return HttpResponse('Hey! Add the course to the correct semester before you add this section to your list! %s')
    MySection.objects.get_or_create(mycourse=mycourse, section=section)
    return HttpResponseRedirect('/students/mycourses/')


@login_required
def remove_mycourse(request, id):
    MyCourse.objects.get(user=request.user, id=id).delete()
    return HttpResponseRedirect('/')

@login_required
def email_courses_for_term(request, semester, year):
    mycourses = MyCourse.objects.filter(user=request.user, offering__semester__exact=semester, offering__year__exact=year)
    return email_courses(request.user.username, mycourses, semester, year)

def email_courses(username, mycourses, semester, year):
    message = "%s's courses for %s %s: \n\n" % (username, semester, year)
    for myc in mycourses:
        c = myc.offering.course
        #message = message + c.dep + c.num + ': ' + c.title + ' - ' + 'http://registrar1.princeton.edu/course/upcome/level/Results.cfm?DEPT=' + c.dep + '&CRSNUM1=' + c.num + ' \n\n'
        message = '%s%s %s: %s - http://registrar1.princeton.edu/course/upcome/level/Results.cfm?DEPT=%s&CRSNUM1=%s\n\n' % (message, c.dep, c.num, c.title, c.dep, c.num)

    sender = 'Princeton Student Course Guide <scg@princeton.edu>'
    receivers = [username+'@princeton.edu', 'scg@princeton.edu']
    send_mail('Courses', message, sender, receivers, fail_silently=False)

    return HttpResponseRedirect('/')
