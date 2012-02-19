# Create your views here.

from django.http import HttpResponse
from django.http import QueryDict
from django.db.models import Q
from ptx.models import Book, Offer, User, Course, Request
from ptx.ptxrender import render_to_response
from ptx.ptxlogin import logged_in
from ptx.bookdata2 import cleanisbn

def classlistings(request):
    course_list = Course.objects.all().order_by('dept', 'num')

    # Dictionary for displaying stuff on template
    dict = {'course_list': course_list}

    # Render to template
    return render_to_response(request, 'ptx/browsebycourse.html', dict)

def browse_class(request, dept, num):
    numstr = str(num)
    book_list = Book.objects.filter(Q(course__dept=dept) &
                                    Q(course__num=num))

    course = Course()
    courses = Course.objects.filter(Q(dept=dept) & Q(num=num))
    if len(courses) > 0:
        course = courses[0]

    num_books = len(book_list)

    # Dictionary for displaying stuff on template
    dict = {'course': course,
            'showofferings': course.hasofferings(),
            'book_list': book_list,
            'showunoffered': course.hasunofferedbooks(),
            'num_books': num_books}

    # Render to template
    return render_to_response(request, 'ptx/browsebooks.html', dict)

def browse_isbn(request, isbn):
    offer_list = Q(book__isbn13=isbn) & Q(status='o')
    offer_list = Offer.objects.filter(offer_list).order_by('price')
    num_books = len(offer_list)

    book = Book()
    books = Book.objects.filter(isbn13=isbn)
    if len(books) > 0:
        book = books[0]

    dict = {'book': book,
            'offer_list': offer_list,
            'num_books': num_books,
            'logged_in': logged_in(request)}

    return render_to_response(request, 'ptx/browsebyisbn.html', dict)

def search(request):
    """Given a search query argument, treats each token as another
    filter on the set of all books. Two types of filters are
    recognized: ISBN and strings."""

    book_list = Book.objects.all()
    st = request.GET.get("s")

    if st:
        # Progressively whittle down the entire book_list.
        for token in st.split():
            clean_isbn = cleanisbn(token)
            if len(clean_isbn) > 0:
                query = Q(isbn13__icontains=clean_isbn)
                query = query | Q(isbn10__icontains=clean_isbn)
            else:
                query = Q(title__icontains=token)
                query = query | Q(author__icontains=token)
                query = query | Q(course__dept__icontains=token)
                query = query | Q(course__num__icontains=token)

            book_list = book_list.filter(query)

    book_list     = book_list.distinct().order_by('title')
    showofferings = any(book.hasOfferings() for book in book_list)
    showunoffered = any(not book.hasOfferings() for book in book_list)

    # Dictionary for displaying stuff on template
    data = {'book_list': book_list,
            'showofferings': showofferings,
            'showunoffered': showunoffered,
            'num_books': len(book_list),
            'st': st}

    # Render to template
    return render_to_response(request, 'ptx/browsebooks.html', data)
