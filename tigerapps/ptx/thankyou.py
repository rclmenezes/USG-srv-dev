# Create your views here.

from django.http import HttpResponse
from django.http import QueryDict
from django.db.models import Q
from ptx.models import Book, Offer, User, Course, Request
from ptx.ptxrender import render_to_response


def offer(request):

    # display thank you message
    if request.method != 'GET':
        raise PermissionDenied()
    
    q = request.GET
    if q.__contains__("b"):
        book_name = q.__getitem__("b")
    else:
        book_name = ""

    # Dictionary for displaying stuff on template
    dict = {'book_name': book_name}

    # Render to template
    return render_to_response(request, 'ptx/offerthankyou.html', dict)

def request(request):

    # display thank you message                                                                        
    if request.method != 'GET':
        raise PermissionDenied()

    q = request.GET
    if q.__contains__("b"):
        book_name = q.__getitem__("b")
    else:
        book_name = ""

    # Dictionary for displaying stuff on template                                                      
    dict = {'book_name': book_name}

    # Render to template                                                                               
    return render_to_response(request, 'ptx/requestthankyou.html', dict)
