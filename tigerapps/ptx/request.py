import uuid
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.http import QueryDict
from django import forms
from django.db.models import Q
from django.contrib.formtools.wizard import FormWizard
from django.core.exceptions import PermissionDenied

from ptx.ptxrender import render_to_response
from ptx.models import Request, Offer, Book, Course, User
from ptx.bookdata2 import book_details, cleanisbn

COURSE = re.compile(r'^\s*([a-zA-Z]{1,3})\s?([0-9]{3})\s*$')
PROCESS_COURSE_FORM, PROCESS_BOOK_FORM, PROCESS_REQUEST_FORM, PROCESS_ADD_BOOK = range(4)

class ChooseCourseForm(forms.Form):
    PROC = PROCESS_COURSE_FORM
    course = forms.RegexField(regex=COURSE)

class ChooseBookForm(forms.Form):
    PROC = PROCESS_BOOK_FORM

    # this field is automatically generated based on the input
    # from ChooseCourseForm
    isbn_from_db = forms.ModelChoiceField(
        widget=forms.RadioSelect(),
        queryset=Book.objects.all(),
        empty_label="Other (Input Below)",
        required=False)
    isbn_from_user = forms.CharField(required=False)

    def __init__(self, course, fields=None):
        super(ChooseBookForm, self).__init__(fields)
        self.fields['isbn_from_db'].queryset = Book.objects.filter(course__exact = course)

class RequestForm(forms.ModelForm):
    PROC = PROCESS_REQUEST_FORM

    class Meta:
        model = Request
        fields = ('maxprice')

class AddBookForm(forms.ModelForm):
    PROC = PROCESS_ADD_BOOK

    class Meta:
        model = Book
        fields = ('isbn13', 'isbn10', 'title', 'desc', 'author', 'edition', 'year', 'publisher', 'list_price')

def reset_request_session(request, ticket):
    '''Clear the session information for this ticket'''
    for k in request.session.keys():
        if ticket in k:
            del request.session[k]

# TODO: CREATE A TICKET ABSTRACTION LAYER


def render_form(form, message, ticket, request):
    return render_to_response(request, 'ptx/request.html', {'form': form, 'proc': form.PROC,
                                             'message':message, 'ticket':ticket} )

def render_bookinfo(bookinfo, ticket, request):
    '''a special form for confirming the book information'''
    return render_to_response(request, 'ptx/request_bookinfo.html', {'bookinfo': bookinfo,
            'proc': PROCESS_ADD_BOOK,
            'ticket':ticket} )

def set_ticket_attr(request, ticket, attr, val):
    request.session['request_' + attr + '_' + ticket] = val

def get_ticket_attr(request, ticket, attr):
    return request.session['request_' + attr + '_' + ticket]

def process(request, step, ticket):
    # this function only processes POST requests
    if request.method != 'POST':
        raise PermissionDenied()

    step = int(step)

    if step == ChooseCourseForm.PROC:
        form = ChooseCourseForm(request.POST)

        if form.is_valid():
            # break down the course input
            course = form.cleaned_data['course']
            m = COURSE.match(course).groups()
            course_dept = m[0].upper()
            course_num = int(m[1])

            # does it exist? if not, add it
            # TODO: MORE CHECKING HERE FOR INVALID DEPARTMENTS, ETC
            course_list = Course.objects.filter(dept__exact=course_dept, num__exact=course_num)
            if len(course_list) == 1:
                c = course_list[0]
            elif len(course_list) == 0:
                c = Course(dept=course_dept, num=course_num)
                c.save()
            else:
                # This can't really happen
                raise PermissionDenied

            # save the internal course id for later
            request.session['request_course_' + ticket] = c

            # show the list of books for the course
            return render_form(ChooseBookForm(c), '', ticket, request)

        else:
            return render_form(ChooseCourseForm(request.POST), '', ticket, request)

    elif step == ChooseBookForm.PROC:
        course = request.session['request_course_' + ticket]
        form = ChooseBookForm(course, request.POST)

        if form.is_valid():
            isbn_from_db = form.cleaned_data['isbn_from_db']
            isbn_from_user = form.cleaned_data['isbn_from_user']

            if isbn_from_db != None:
                # book exists already, let the user list this book
                request.session['request_book_' + ticket] = isbn_from_db
                return render_form(RequestForm(), '', ticket, request)

            elif isbn_from_user != None:
                # check if book exists in DB, just not associated with that class
                if Book.objects.filter(isbn13=isbn_from_user).count() == 0:
                    # book does not exist, let the user create it
                    #form = AddBookForm()
                    #form.fields['isbn13'].initial = isbn_from_user
                    bookinfo = book_details(isbn_from_user)
                    if bookinfo == None:
                        return render_form(form, '', ticket, request)
                    else:
                        set_ticket_attr(request, ticket, 'bookinfo', bookinfo)
                        return render_bookinfo(bookinfo, ticket, request)
                else:
                    # book needs new class reference added.
                    book = Book.objects.get(isbn13=isbn_from_user)
                    book.course.add(course)
                    book.save()
                    request.session['request_book_' + ticket] = book
                    return render_form(RequestForm(), '', ticket, request)

            else:
                # no book chosen, go back and make the user choose a book
                return render_form(form, '', ticket, request)

        else:
            return render_form(form, '', ticket, request)

    elif step == PROCESS_ADD_BOOK:
        bookinfo = get_ticket_attr(request, ticket, 'bookinfo')

        # TODO: MAKE SURE AGAIN THAT THE ISBN IS NOT ALREADY IN THE DATABASE
        book = Book(
                isbn13  = bookinfo['isbn13'],
                isbn10  = bookinfo['isbn10'],
                title   = bookinfo['title'],
                desc  = '',
                author  = bookinfo['author'],
                edition  = bookinfo['edition'],
                year   = bookinfo['year'],
                publisher   = bookinfo['publisher'],
                list_price   = 0,
                imagename = bookinfo['img_name'])

        course = request.session['request_course_' + ticket]
        book.course.add(course)
        book.save()

        request.session['request_book_' + ticket] = book

        return render_form(RequestForm(), '', ticket, request)

    elif step == RequestForm.PROC:
        form = RequestForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data

            book = request.session['request_book_' + ticket]
            user, created = User.objects.get_or_create(net_id=request.user.username)
            maxprice = form.cleaned_data['maxprice']
            the_request = Request(
                    book=book,
                    user=user,
                    maxprice=maxprice)

            the_request.save()

            reset_request_session(request, ticket)

            # redirect to thank you page
            return HttpResponseRedirect('/request/thankyou?b=%s' % (book))

        else:
            return render_form(form, '', ticket, request)

    return HttpResponse(step)

def offer(request, ticket=''):
    # TEMPORARY HACK
    #ticket = uuid.uuid4().hex
    #return render_form(ChooseCourseForm(), '', ticket, request)

    if request.user.is_authenticated():
        ticket = uuid.uuid4().hex
        return render_form(ChooseCourseForm(), '', ticket, request)

    else:
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'Offer a book',
                                   'redirect_url': '/offer'} )


def request(request, ticket=''):
    if request.user.is_authenticated():
        ticket = uuid.uuid4().hex
        return render_form(ChooseCourseForm(), '', ticket, request)

    else:
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'Request a book',
                                   'redirect_url': '/request'} )
