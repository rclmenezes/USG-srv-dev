from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.cache import cache
from apps.courses.models import Offering, Course, CrossList, THIS_YEAR, THIS_SEMESTER, NEXT_SEMESTER, NEXT_YEAR
from apps.professors.models import Professor
from apps.students.models import RecentCourses, RecentDepartments, MyCourse
from apps.reviews.models import CourseReview, ProfessorReview

def search_professors(q):
    return Professor.objects.filter(last_name__icontains=q)

@login_required
def search(request):
    professors = None

    q = request.GET.get('q','').strip(" \r\n-'")

    if q:
        professors = search_professors(q)

    return render_to_response('professors/search_results.html', {'professors':professors,'q':q,'NEXT_SEMESTER':NEXT_SEMESTER,'NEXT_YEAR':NEXT_YEAR,'THIS_SEMESTER':THIS_SEMESTER,'THIS_YEAR':THIS_YEAR,}, context_instance = RequestContext(request))

