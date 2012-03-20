from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.cache import cache
from apps.courses.models import Offering, Course, CrossList, THIS_YEAR, THIS_SEMESTER, NEXT_SEMESTER, NEXT_YEAR
from apps.students.models import RecentCourses, RecentDepartments, MyCourse
from apps.reviews.models import CourseReview, ProfessorReview

from apps.elearn.models import TestFile
from django import forms

def post(request):
    if request.method == 'POST':
        manipulator = TestFile.AddManipulator()
        new_data = request.POST.copy()
        new_data.update(request.FILES)  # This has to be added

        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            new_message = manipulator.save(new_data)

    files = TestFile.objects.all()

    return render_to_response('elearn/post.html', {'files':files}, context_instance = RequestContext(request))
