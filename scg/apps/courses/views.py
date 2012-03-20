from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.cache import cache
from apps.courses.models import Offering, BlackBoard, Course, CrossList, THIS_YEAR, THIS_SEMESTER, NEXT_SEMESTER, NEXT_YEAR
from apps.students.models import RecentCourses, RecentDepartments, MyCourse
from apps.reviews.models import CourseReview, ProfessorReview

from apps.professors.views import search_professors

distribution_requirements = ['EC','EM','HA','LA','QR','SA','ST','STX','W']
departments = ['AAS', 'AFS', 'AMS', 'ANT', 'AOS', 'APC', 'ARA', 'ARC', 'ART', 'AST', 'CEE', 'CHE', 'CHI', 'CHM', 'CHV', 'CLA', 'CLG', 'COM', 'COS', 'CWR', 'DAN', 'EAS', 'ECO', 'ECS', 'EEB', 'EGR', 'ELE', 'ENG', 'ENV', 'EPS', 'FIN', 'FRE', 'FRS', 'GEO', 'GER', 'HEB', 'HIN', 'HIS', 'HLS', 'HOS', 'HUM', 'ITA', 'JDS', 'JPN', 'JRN', 'KOR', 'LAS', 'LAT', 'LIN', 'MAE', 'MAT', 'MED', 'MOL', 'MSE', 'MUS', 'NES', 'ORF', 'PAW', 'PER', 'PHI', 'PHY', 'POL', 'POP', 'POR', 'PSY', 'REL', 'RUS', 'SLA', 'SOC', 'SPA', 'STC', 'SWA', 'THR', 'TPP', 'TUR', 'VIS', 'WOM', 'WRI', 'WWS']

@login_required
def search(request):
    import re
    courses = None
    q = request.GET.get('q','').strip(" \r\n-'")

    if q:
        m = re.match('^([a-zA-Z]{3}) ?([0-9]+[a-zA-Z]?)?$',q)
        if m:
            if m.group(2):
                #course dep/num search
                courses = Course.objects.filter(crosslist__dep=m.group(1), crosslist__num=m.group(2))
            else:
                #course dep search
                return HttpResponseRedirect('/courses/dept/%s/' % m.group(1).upper())
        else:
            professors = search_professors(q)
            if professors:
                #professor search
                return render_to_response('professors/search_results.html', {'professors':professors,'q':q,'NEXT_SEMESTER':NEXT_SEMESTER,'NEXT_YEAR':NEXT_YEAR,'THIS_SEMESTER':THIS_SEMESTER,'THIS_YEAR':THIS_YEAR,}, context_instance = RequestContext(request))
            else:
                #course title search
                courses = Course.objects.filter(title__icontains=q)

    #redirect to one specific course if only one
    if courses and len(courses) == 1:
        return HttpResponseRedirect(courses[0].get_absolute_url())

    return render_to_response('courses/search_results.html', {'courses':courses,'q':q}, context_instance = RequestContext(request))

@login_required
def dr(request, dr=None):
    courses = None

    if dr != 'ALL':
        #courses = Course.objects.filter(dr=dr).filter(semester='S').filter(year='2007')
        courses = Course.objects.filter(dr=dr)

    return render_to_response('courses/dr.html', {'courses':courses,'dr':dr}, context_instance = RequestContext(request))

@login_required
def blackboard(request, cid=None):
    c = Course.objects.get(cid=cid)
    black_board, _ = BlackBoard.objects.get_or_create(course=c, defaults={'text':BlackBoard.default_message})
    if request.method == 'GET':
        return HttpResponse(black_board.text)
    elif request.method == 'POST':
        text = request.POST['board']
        text.replace('<', '&lt;')
        text.replace('>', '&gt;')
        black_board.text = text
        black_board.save()
        return HttpResponse('')
    else:
        raise Exception('Neither GET nor POST?')

@login_required
def course_detail(request, cid=None):
    c = Course.objects.get(cid=cid)

    course_reviews = CourseReview.objects.filter(course = c)

    professor_reviews = []
    for professor in c.professors.all():
        professor_reviews = ProfessorReview.objects.filter(professor__pid = professor.pid)

    try:
        o = Offering.objects.get(course=c, year=NEXT_YEAR, semester=NEXT_SEMESTER)
        sections = o.section_set.all()
    except:
        sections = None

    #add this as a recent course or update time last viewed
    rc = RecentCourses.objects.get_or_create(user=request.user, course=c)
    if not rc[1]:
        rc[0].save()

    data = {'c':c,
            'course_reviews':course_reviews,
            'professor_reviews':professor_reviews,
            'sections':sections,
            'NEXT_SEMESTER':NEXT_SEMESTER,
            'NEXT_YEAR':NEXT_YEAR,
            'THIS_SEMESTER':THIS_SEMESTER,
            'THIS_YEAR':THIS_YEAR,
            }
    return render_to_response('courses/course_detail.html',
                              data,
                              context_instance = RequestContext(request))

@login_required
def dept(request, dept=None):
    """ View for /courses/dept/___/. """

    courses = None

    if dept != 'ALL':
        courses = CrossList.objects.courses_in_dep(dept)

        rd = RecentDepartments.objects
        rd = rd.get_or_create(user=request.user, department=dept)
        if not rd[1]:
            rd[0].save()

    data = {'courses':courses,
            'departments':departments,
            'department':dept
            }
    return render_to_response('courses/dept.html', data,
                              context_instance = RequestContext(request))

@login_required
def index(request):
    #cache recentcourses for speed
    #recent_courses = cache.get(request.user.username+'_recent_courses')
    #if not recent_courses:
    recent_courses = RecentCourses.objects.recent_courses(request.user, 10)
    #    cache.set(request.user.username+'_recent_courses',recent_courses,60*30)

    #cache popular_courses for speed
    popular_courses = cache.get('popular_courses')
    if not popular_courses:
        popular_courses = RecentCourses.objects.popular_courses()
        cache.set('popular_courses', popular_courses, 60 * 60)

    recent_departments = RecentDepartments.objects.recent_departments(request.user)

    #cache mycourses for speed
    #mycourses = cache.get(request.user.username+'_mycourses')
    #if not mycourses:
    mycourses = MyCourse.objects.filter(user=request.user)
    #    cache.set(request.user.username+'_mycourses', mycourses, 60 * 30)

    return render_to_response('courses/index.html', {'recent_courses':recent_courses, 'popular_courses':popular_courses, 'recent_departments':recent_departments,'mycourses':mycourses,'NEXT_SEMESTER':NEXT_SEMESTER,'NEXT_YEAR':NEXT_YEAR,'THIS_SEMESTER':THIS_SEMESTER,'THIS_YEAR':THIS_YEAR,}, context_instance = RequestContext(request))
