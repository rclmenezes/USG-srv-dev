import django.utils.simplejson as json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.courses.models import Course
from apps.reviews.models import CourseReview

def response(data):
    return HttpResponse(json.dumps(data), mimetype='text/plain')

def course(request, dep=None, num=None):
    try:
        c = Course.objects.get(dep=dep.lower(), num=num)
        r = CourseReview.objects.filter(course=c)
    except Course.DoesNotExist:
        return response(dict(error=u'invalid course'))

    first, second = None, None
    if len(r) >= 1:
        first = r[0].comment
    if len(r) >= 2:
        second = r[1].comment

    data = {
        'first': first,
        'second': second,
        'link': reverse('apps.courses.views.course_detail', args=[c.cid]),
        'gpa': unicode(c.gpa),
        }
    return response(data)
