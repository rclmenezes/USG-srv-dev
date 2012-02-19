from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect

class ProcessPermDenied:
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            return HttpResponseRedirect('/')
        return None
