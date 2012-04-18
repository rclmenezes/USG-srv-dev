# Create your views here.

from django.http import HttpResponse
from django.http import QueryDict
from django.db.models import Q
from ptx.models import Book, Offer, Request
from ptx.ptxlogin import logged_in
from ptx.navbar import getnavbar
from ptx.ptxrender import render_to_response

def homepage(request):
    # order by id (desc) rather than date because ids are uniquely created in ascending order,
    # whereas dates are non-unique
    new_offers = Offer.objects.filter(status='o').order_by('-id')
    new_books_offered = []
    for offer in new_offers:
        book = offer.book
        if not book in new_books_offered:
            new_books_offered.append(book)
        if len(new_books_offered) == 5:
            break
    
    req_with_offers = None
    name = None
    num_pending_trans = None
    rating = None
    num_open_offers = None
    if logged_in(request):
        wishlist = Request.objects.filter(user=request.session['user_data'], status='o')
        req_with_offers = []
        for req in wishlist:
            if req.book.hasOfferings():
                req_with_offers.append(req)

        name = request.session['user_data'].first_name

        num_pending_trans = Request.objects.filter(user=request.session['user_data'], status='p').count() + \
                            Offer.objects.filter(user=request.session['user_data'], status='p').count()

        num_open_offers = Offer.objects.filter(user=request.session['user_data'], status='o').count()
        rating = request.session['user_data'].getRating()
    

    # Dictionary for displaying stuff on template
    dict = { 
        'logged_in': logged_in(request),
        'name': name, 
        'new_books_offered': new_books_offered,
        'num_pending_trans': num_pending_trans,
        'req_with_offers': req_with_offers,
        'num_open_offers': num_open_offers,
        'rating': rating,
    }

    # Render to template
    return render_to_response(request, 'ptx/homepage.html', dict)
