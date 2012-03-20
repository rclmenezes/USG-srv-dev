from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from apps.courses.models import Course
from apps.professors.models import Professor
from apps.students.models import StudentDepartment
from apps.reviews.models import CourseReview, ProfessorReview
from apps.reviews.forms import DecimalField, RequiredForm, CourseForm, ProfessorForm
from apps.courses.views import departments

def course_reviews(request, cid):
    cr = CourseReview.objects.filter(course__cid = cid)
    return render_to_response('reviews/course_reviews.html', {'reviews':cr,'cid':cid}, context_instance = RequestContext(request))

def professor_reviews(request, pid):
    pr = ProfessorReview.objects.filter(professor__pid = pid)
    return render_to_response('reviews/professor_reviews.html', {'reviews':pr,'pid':pid}, context_instance = RequestContext(request))

def post_review(request):
    pid = request.GET.get('pid',None)
    cid = request.GET.get('cid',None)

    if request.method == 'POST':
        required_form = RequiredForm(request.POST, auto_id=False)
        course_form = CourseForm(request.POST, auto_id=False, prefix='course')
        professor_form = ProfessorForm(request.POST, auto_id=False, prefix='professor')
    else:
        department = StudentDepartment.objects.get_or_create(user=request.user, defaults={'department':''})[0].department
        initial={'department':department,'pid':pid,'cid':cid}

        required_form = RequiredForm(auto_id=False, initial=initial)
        course_form = CourseForm(auto_id=False, prefix='course')
        professor_form = ProfessorForm(auto_id=False, prefix='professor')

    if required_form.is_valid() and course_form.is_valid() and professor_form.is_valid():
        sd = StudentDepartment.objects.get_or_create(user=request.user, defaults={'department':required_form.cleaned_data['department']})
        if not sd[1]:
            sd[0].department = required_form.cleaned_data['department']
            sd[0].save()

        if course_form.cleaned_data['q1'] != u'': c = True
        else: c = False
        if professor_form.cleaned_data['q1'] != u'': p = True
        else: p = False

        all_data = {}
        all_data['user'] = request.user
        all_data.update(required_form.cleaned_data)
        all_data.update({'course': Course.objects.get(pk=all_data['cid'])})
        all_data.update({'professor':Professor.objects.get(pk=all_data['pid'])})
        del(all_data['cid'])
        del(all_data['department'])
        del(all_data['pid'])

        if c:
            data = {}
            data.update(all_data)
            data.update(course_form.cleaned_data)
            course_review = CourseReview.objects.get_or_create(user=data['user'], course=data['course'], defaults=data)[0]
            course_review.__dict__.update(data)
            course_review.save()
        if p:
            data = {}
            data.update(all_data)
            data.update(professor_form.cleaned_data)
            professor_review = ProfessorReview.objects.get_or_create(user=data['user'], professor=data['professor'], defaults=data)[0]
            professor_review.__dict__.update(data)
            professor_review.save()

        if c: return HttpResponseRedirect(course_review.course.get_absolute_url())
        if p: return HttpResponseRedirect(professor_review.professor.get_absolute_url())

        return HttpResponseRedirect('/')

    return render_to_response('reviews/post.html', {'required_form':required_form, 'course_form':course_form, 'professor_form':professor_form}, context_instance = RequestContext(request))
