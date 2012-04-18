from django import forms  

from ptx.ptxrender import render_to_response
from ptx.ptxlogin import logged_in
from ptx.models import Request, Book, User
from ptx.models import Request, Book, User
from ptx.bookdata2 import book_details, cleanisbn

class AddForm(forms.Form):
    '''A form that processes the GET requests to wishlist'''
    # isbn of book to add
    add = forms.CharField(max_length=32, label='ISBN', required=False)

class DelForm(forms.Form):
    '''A form that processes the GET requests to wishlist'''
    # isbn of book to add
    delete = forms.IntegerField(required=False)

class AlreadyInWishlist(Exception):
    pass

def process_add(request, form_data):
    '''Returns the added book if add is successful, None if the field is blank, 
    or raises Book.DoesNotExist if no such book is found'''

    form = AddForm(form_data)

    if not form.is_valid():
        raise Book.DoesNotExist

    # Clean up the ISBN, or stop if there has been no ISBN entered
    isbn = form.cleaned_data['add']
    if len(isbn) == 0: return None
    isbn = cleanisbn(isbn)

    # Get the book, or raise the exception that it does not exist
    if len(isbn) == 13: 
        try:
            book = Book.objects.get(isbn13=isbn)
        except Book.DoesNotExist:
            book = book_details(isbn)
            if book != None: book.save()
            else: raise Book.DoesNotExist

    elif len(isbn) == 10: 
        try:
            book = Book.objects.get(isbn10=isbn)
        except Book.DoesNotExist:
            book = book_details(isbn)
            if book != None: book.save()
            else: raise Book.DoesNotExist

    else:
        raise Book.DoesNotExist

    # Check that the item is not already in the wishlist
    req_list = Request.objects.filter(user=request.session['user_data'],
            status='o', book=book)
    if len(req_list) > 0:
        raise AlreadyInWishlist

    req = Request(user=request.session['user_data'], book = book, status = 'o', maxprice = 0)
    req.save()

    return book


def process_del(request, form_data):
    '''Deletes the request from the database, or silently fails'''
    form = DelForm(form_data)

    if not form.is_valid():
        return

    id = form.cleaned_data['delete']
    if id == None:
        return

    # make sure the request belongs to the user
    req_list = Request.objects.filter(id=id, user=request.session['user_data'])
    if len(req_list) == 0:
        return

    req_list[0].delete()


 
def wishlist(request):
    if not logged_in(request):
        return render_to_response(request, 'ptx/needlogin.html', {
                'header_text': 'Wishlist',
                'redirect_url': '/wishlist'})

    # Adding a book?
    add_book = None
    add_error = ''
    try:
        add_book = process_add(request, request.GET)
    except Book.DoesNotExist:
        add_error = 'The ISBN you entered does not exist'
    except AlreadyInWishlist:
        add_error = 'This book is already in your wishlist!'
        

    # Deleting a book?
    process_del(request, request.GET)

    # Render the page
    req_list = Request.objects.filter(user=request.session['user_data'],
            status='o')

    return render_to_response(request, 'ptx/wishlist.html', { 
            'add_form': AddForm(),
            'add_error': add_error,
            'book': add_book,
            'req_list': req_list
            } )

