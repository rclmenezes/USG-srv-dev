import re
import uuid
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.http import QueryDict
from django import forms
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe

from ptx.ptxrender import render_to_response
from ptx.models import Offer, Book, Course, User
from ptx.ptxlogin import logged_in
from ptx.bookdata2 import book_details, cleanisbn
from ptx.dept import is_valid_dept

COURSE_REGEX = re.compile(r'^\s*([a-zA-Z]{1,3})\s?([1-5]\d\d)\s*$')
YEAR_REGEX = r'^20[0-9][0-9]$'
MIN_YEAR = 2000

PROCESS_COURSE_FORM, PROCESS_BOOK_FORM, PROCESS_OFFER_FORM, PROCESS_ADD_BOOK = range(4)

CONDITION_CHOICES_WITH_DESC = (
    ('a', mark_safe('<b>New</b>: Brand new, never been used, and in perfect condition. Still in shrink-wrap, if applicable.')),
    ('b', mark_safe('<b>Like New</b>: Looks new and in perfect condition. No markings whatsoever.')),
    ('c', mark_safe('<b>Very Good</b>: Excellent condition with slight wear-and-tear. Very sparse markings.')),
    ('d', mark_safe('<b>Good</b>: Clean condition with moderate wear-and-tear. Limited markings.')),
    ('e', mark_safe('<b>Acceptable</b>: Usable condition, with heavier signs of wear-and-tear and a considerable amount of markings.')),
)


class BookChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return mark_safe("<img src='%s'><b>%s</b><br><i>%s</i>" % (obj.imagename, obj.title, obj.author))

class ChooseCourseForm(forms.Form):
    PROC = PROCESS_COURSE_FORM
    course = forms.CharField()

    def clean_course(self):
        course = self.cleaned_data['course']
        course = course.replace(u' ', u'')
        if course == '#misc':
            return course

        m = COURSE_REGEX.match(course)
        if not m:
            raise forms.ValidationError('The course you entered is invalid')

        course_dept = m.group(1).upper()
        if not is_valid_dept(course_dept):
            raise forms.ValidationError('The department you entered is invalid.')

        return course

class ChooseBookForm(forms.Form):
    isbn = forms.CharField(max_length=32, widget=forms.HiddenInput)

    def clean_isbn(self):
        '''Converts the user inputted isbn into a valid ISBN-13, or
           raises a validation error if the isbn does not exist or is
           incorrectly formatted'''

        # check formatting
        isbn = cleanisbn(self.cleaned_data['isbn'])
        if isbn == '':
            raise forms.ValidationError('The ISBN you entered is not valid')

        # check if book exists either here at PTX or at amazon
        try:
            if len(isbn) == 13:
                book = Book.objects.get(isbn13=isbn)
            elif len(isbn) == 10:
                book = Book.objects.get(isbn10=isbn)

        except Book.DoesNotExist:
            # book does not exist in PTX, so try fetching it from amazon
            book = book_details(isbn)
            if book == None:
                raise forms.ValidationError('A book with this ISBN could not be found')
            book.save()

        return book.isbn13

class InputBookForm(ChooseBookForm):
    '''Same as ChooseBookForm but the ISBN field is not hidden'''
    isbn = forms.CharField(max_length=32, label="ISBN")

class OfferForm(forms.ModelForm):
    PROC = PROCESS_OFFER_FORM
    condition = forms.ChoiceField(widget=forms.RadioSelect,
                                  choices=CONDITION_CHOICES_WITH_DESC)
    year = forms.RegexField(regex=YEAR_REGEX,
                            max_length=4)

    def clean_year(self):
        year = int(self.cleaned_data['year'])
        now = datetime.now()
        if year > now.year or year < MIN_YEAR:
            raise forms.ValidationError('The year you entered is not valid.')

        return str(year)


    class Meta:
        model = Offer
        fields = ('price', 'condition', 'desc', 'semester', 'year')

def reset_offer_session(request, ticket):
    '''Clear the session information for this ticket'''
    for k in request.session.keys():
        if ticket in k:
            del request.session[k]


def render_form(form, message, ticket, request):
    return render_to_response(request, 'ptx/offer.html', {'form': form, 'proc': form.PROC,
                                             'message':message, 'ticket':ticket} )

def render_choosecourse(form_data, ticket, request):
    return render_to_response(request, 'ptx/offer_choosecourse.html', {
            'form': ChooseCourseForm(form_data),
            'proc': PROCESS_COURSE_FORM,
            'ticket':ticket} )


def render_choosebook(book_list, form_data, ticket, request):
    extended_book_list = []
    for book in book_list:
        form = ChooseBookForm({'isbn': book.isbn13})
        extended_book_list.append((book, form))

    # It's pointless to show so many books at once.
    if len(extended_book_list) > 20:
        extended_book_list = []

    return render_to_response(request, 'ptx/offer_choosebook.html', {
            'book_list': extended_book_list,
            'default_form': InputBookForm(form_data),
            'proc': PROCESS_BOOK_FORM,
            'ticket':ticket} )


def render_bookinfo(book, ticket, request):
    '''a special form for confirming the book information'''
    return render_to_response(request, 'ptx/offer_bookinfo.html', {'book': book,
            'prev_proc': PROCESS_COURSE_FORM,
            'proc': PROCESS_ADD_BOOK,
            'ticket':ticket} )

def render_offerinfo(book, form_data, ticket, request):
    return render_to_response(request, 'ptx/offer_offerinfo.html', {
            'book': book,
            'form': OfferForm(form_data),
            'proc': PROCESS_OFFER_FORM,
            'ticket': ticket} )

# Ticket abstraction layer for sessions
def set_ticket_attr(request, ticket, attr, val):
    request.session['offer_' + attr + '_' + ticket] = val

def get_ticket_attr(request, ticket, attr):
    key = 'offer_' + attr + '_' + ticket
    if key in request.session:
        return request.session[key]
    else:
        # the key is somehow invalid. this is usually because the
        # ticket has expired.
        raise PermissionDenied()

# View processing
def process_course_form(form_data, request, ticket):
    form = ChooseCourseForm(form_data)

    if not form.is_valid():
        return render_choosecourse(form_data, ticket, request)

    # break down the course input
    course = form.cleaned_data['course']
    if course == '#misc':
        course_dept = '#misc'
        course_num  = '000'
    else:
        m = COURSE_REGEX.match(course).groups()
        course_dept = m[0].upper()
        course_num = int(m[1])

    course, created = Course.objects.get_or_create(dept=course_dept, num=course_num)

    # save the internal course id for later
    set_ticket_attr(request, ticket, 'course', course)

    # show the list of books for the course
    book_list = Book.objects.filter(course = course)
    return render_choosebook(book_list, None, ticket, request)


def process(request, step, ticket):

    # as a security measure, this function only processes POST requests
    if request.method != 'POST':
        raise PermissionDenied()

    step = int(step)

    if step == PROCESS_COURSE_FORM:
        return process_course_form(request.POST, request, ticket)

    elif step == PROCESS_BOOK_FORM:
        form = ChooseBookForm(request.POST)
        course = get_ticket_attr(request, ticket, 'course')
        book_list = Book.objects.filter(course = course)

        if not form.is_valid():
            # no book chosen, go back and make the user choose a book
            return render_choosebook(book_list, request.POST, ticket, request)

        isbn13 = form.cleaned_data['isbn']

        book = Book.objects.get(isbn13=isbn13)
        set_ticket_attr(request, ticket, 'book', book)
        return render_offerinfo(book, None, ticket, request)

    elif step == PROCESS_OFFER_FORM:
        form = OfferForm(request.POST)

        book = get_ticket_attr(request, ticket, 'book')
        course = get_ticket_attr(request, ticket, 'course')
        user = request.session['user_data']

        if not form.is_valid():
            return render_offerinfo(book, request.POST, ticket, request)


        # associate the book and the course
        book.course.add(course)
        book.save()

        # save the offer
        f = form.cleaned_data
        offer = Offer(
                book=book,
                user=user,
                status='o',
                type='s', # SELLING ONLY
                allow_bids=False, # NO BIDS
                price=f['price'],
                condition=f['condition'],
                desc=f['desc'],
                semester=f['semester'],
                year=f['year'])
        offer.save()

        # clean the ticket data so that user doesn't add another listing if he/she refreshes the page
        reset_offer_session(request, ticket)

        # show a little confirmation
        return render_to_response(request, u'ptx/offerthankyou.html', {'offer': offer, 'course': course})

    else:
        # a fallback for posts to invalid steps
        raise PermissionDenied()

def offer(request, ticket=''):
    if not logged_in(request):
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'Offer a Book',
                                   'redirect_url': '/offer'} )

    # create a new ticket for the user so that simultaneous offerings from the same
    # user gets handled correctly
    ticket = uuid.uuid4().hex

    if 'course' in request.GET:
        # automatic course processing if /offer?course=<course> is specified in the URL
        return process_course_form(request.GET, request, ticket)

    else:
        # standard processing
        return render_choosecourse(None, ticket, request)

