from django.shortcuts import get_object_or_404, render_to_response
from django.core.mail import send_mail
from ttrade.models import *
from ttrade.forms import *
from ttrade.emails import *
from search import *
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import *
import datetime

# Sleazy hack for timezones. Django doesn't have a timezone compatible DateTimeField,
# so this macro should do for now.datetime.datetime.now()

def home(request):
    return showListings(request, Listing.objects.filter(expire__gt=datetime.datetime.now()), 'ttrade/index.html')

@login_required
def yourListings(request):
    return showListings(request, Listing.objects.filter(user=request.user), 'ttrade/yourListings.html', "yourListings/", "Your Listings")

@login_required
def yourOffers(request):
    return showListings(request, Listing.objects.filter(offers__user=request.user), 'ttrade/yourListings.html', "yourOffers/", "Listings you offered on")

@login_required
def create(request):
    if not request.user.is_active:
       return render_to_response('ttrade/baduser.html')
    listingForm = ListingForm()
    if request.method == 'POST':
        listingForm = ListingForm(request.POST, request.FILES)
        if listingForm.is_valid():
            listing = listingForm.save(commit=False)
            listing.user = request.user
            if request.POST['listingType'] == "request":
                listing.listingType = 'R'
            elif request.POST['listingType'] == "rental":
                listing.listingType = 'T'
            elif request.POST['listingType'] == "exchange":
                listing.listingType = 'E'
            else:
                listing.listingType = 'S'
            listing.expire = datetime.datetime.now() + datetime.timedelta(days=int(request.POST['days']), hours=int(request.POST['hours']))
            listing.posted = datetime.datetime.now()
            listing.save()
            return HttpResponseRedirect("/item/" + str(listing.listingID))
    
    return render_to_response('ttrade/create.html', {'logged_in': True, 'listingForm': listingForm, 'hide': True})

def item(request, listingID):
    listing = get_object_or_404(Listing, listingID=listingID)
    
    # Check if logged in
    edit = edited = expiration = False
    if request.user.is_authenticated():
        logged_in = True
        if request.user == listing.user or request.user.is_staff: # Owner of listing
            edit = True
        elif datetime.datetime.now() > listing.expire: # Expire
            title = "Sorry!"
            body = "This post has expired!"
            return render_to_response('ttrade/confirm.html', {'title': title, 'body': body, 'logged_in': logged_in})
    else: # Not logged in
        logged_in = False
    
    # User messages (why make a whole system for two messages, anyway?)
    message = None
    if request.method == 'GET':
        if 'expiration' in request.GET or 'edited' in request.GET:
            message = "Your changes have been made."
            
    if request.method =='POST':
        if 'offer' in request.POST:
            offer = get_object_or_404(Offer, offerID=int(request.POST['offer']))
            if 'Accept' in request.POST:
                title = "Success"
                body = "You have accepted the offer! You and the second party will receive an email shortly."
                buyerConfirmation(listing, offer)
                listerConfirmation(listing, offer)
                if listing.method != 'Mu':
                    listing.expire = datetime.datetime.now()
                    listing.save()
                else:
                    body += " (Tip: Listings that are listed as multiple items and prices only expire when you tell them to.)"
                    listing.offers.remove(offer)
                return render_to_response('ttrade/confirm.html', {'title': title, 'body': body, 'logged_in': logged_in})
            if 'Reject' in request.POST:
                listing.offers.remove(offer)
                listing.save()
                offerRejection(listing, offer)
                message = "That offer has been removed."
    
    # If method is fixed or free
    if listing.method == "Fr" or listing.method == "Fi":
        return render_to_response('ttrade/fixedOrFree.html', {'edit': edit, 'message': message, 'logged_in': logged_in, 'listing': listing})
        
    # If method is anything else (where you make an offer) (this includes requests to buy)
    return render_to_response('ttrade/claim.html', {'edit': edit, 'message': message, 'logged_in': logged_in, 'listing': listing})
 
# Does all the buying
@login_required   
def confirm(request):
    if request.method == 'POST' and 'listing' in request.POST:
        listing = Listing.objects.get(listingID=int(request.POST['listing']))
        if datetime.datetime.now() > listing.expire:
            return HttpResponseRedirect('/')
            
        title = "Success!"
        user = request.user
        price = additional = None
        if listing.method == 'Au':
            price = Decimal(request.POST['price'])
            listing.price = price
            body = "You have made a bid for"
        elif listing.method == 'Fr':
            body = "You have claimed"
            listing.expire = datetime.datetime.now()
        elif listing.method == 'Fi':
            body = "You have bought"
            price = listing.price
            listing.expire = datetime.datetime.now()
        else: # Includes requests to buy
            additional = request.POST['additional']
            body = "You have made an offer for"
        
        offer = Offer(user=user, price=price, additional=additional)
        offer.save()
        listing.offers.add(offer)
        listing.save()
        if listing.method == 'Fr' or listing.method == 'Fi':
            buyerConfirmation(listing, offer)
            listerConfirmation(listing, offer)
        else:
            offerBuyerConfirmation(listing, offer)
            offerListerConfirmation(listing, offer)
        
        body +=  " the listing \"" + listing.title + "\". An email has been sent to both you and the lister."
        return render_to_response('ttrade/confirm.html', {'title': title, 'body': body, 'logged_in': True})
    else:
        return HttpResponseRedirect('/')
 
# Lulzy method
def notYourListing(request):
    title = "Error"
    body = "Er... This isn't your listing. You can't change it."
    return render_to_response('ttrade/confirm.html', {'title': title, 'body': body, 'logged_in': True})

# Change the expiration of a listing  
@login_required  
def expiration(request, listingID):
    listing = Listing.objects.get(listingID=listingID)
    # Lulzy error
    if not request.user.is_staff and request.user != listing.user:
        return notYourListing(request)
    # Make changes and redirect back to item page  
    if request.method == "POST" and 'days' in request.POST and 'hours' in request.POST:
        listing.expire = datetime.datetime.now() + datetime.timedelta(days=int(request.POST['days']), hours=int(request.POST['hours']))
        listing.save()
        return HttpResponseRedirect('/item/' + str(listing.listingID) + '?expiration=True')
    # Blank form
    return render_to_response('ttrade/expiration.html', {'listing': listing, 'logged_in': True})
    
@login_required  
def edit(request, listingID):
    listing = Listing.objects.get(listingID=listingID)
    # Lulzy error
    if not request.user.is_staff and request.user != listing.user:
        return notYourListing(request)
    # Make edits and redirect to item page 
    if request.method == 'POST':
        listingForm = ListingForm(request.POST, request.FILES, instance=listing)
        if listingForm.is_valid():
            listingForm.save()
            return HttpResponseRedirect('/item/' + str(listing.listingID) + '?edited=True')
    # Make blank form
    listingForm = ListingForm(instance=listing)
    return render_to_response('ttrade/edit.html', {'listingID': listing.listingID, 'logged_in': True, 'listingForm': listingForm, 'listingType': listing.listingType})
    
def terms(request):
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    return render_to_response('ttrade/terms.html', {'logged_in': logged_in})
  
# Generic view that does yourListings and index  
def showListings(request, listing_set, template, extension="", list_title="All Listings"):
    # Check if logged in
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
        
    # Get categories for search and appends amount in each category
    choices = CATEGORY_CHOICES
    categories = []
    categories.append(('Al', 'All Categories', len(listing_set)))
    for choice in choices:
        categories.append((choice[0], choice[1], len(listing_set.filter(category=choice[0]))))

    listings_list = listing_set

    # Search (slowly filters by variables). Uses oldGet to maintain mode during pagination
    oldGet = ""
    if 'category' in request.GET:
        category = request.GET['category']
        if category != 'Al':
            listings_list = listings_list.filter(category=category)
            oldGet += "&category=" + category
    else:
        category = None
        
    if 'listingType' in request.GET:
        listingType = request.GET['listingType']
        if listingType != 'A':
            listings_list = listings_list.filter(listingType=listingType)
            oldGet += "&listingType=" + listingType
    else:
        listingType = None  
        
    if 'query' in request.GET:
        query = request.GET['query']
        if query != "" and query.strip() != "": 
            listings_list = listings_list.filter(get_query(query, ['title', 'description']))
            oldGet += "&query=" + query
    else:
        query = None
    
    if 'order' in request.GET:
        order = request.GET['order']
        if order == 'P':
            listings_list = listings_list.order_by('price').exclude(Q(price__isnull=True) | Q(price__exact=0))
        elif order == 'N':
            listings_list = listings_list.order_by('posted').reverse()
        else:
            listings_list = listings_list.order_by('expire')
        oldGet += "&order=" + order
    else:
      listings_list = listings_list.order_by('expire')  
      order = "R"
           
    if 'reverse' in request.GET and request.GET['reverse'] == 'True':
        listings_list = listings_list.reverse()
        reverse = True
    else:
        reverse = False
                
       
    # Pagination 
    if 'items' in request.GET:
        items = int(request.GET['items'])
    else:
        items = 20
    if 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1  
    paginator = Paginator(listings_list, items)
    
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        listings = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        listings = paginator.page(paginator.num_pages)
           
    return render_to_response(template, {'extension': extension, 'reverse': reverse, 'listingType': listingType, 'query': query, 'category': category, 'items': items, 'page': page, 'categories': categories, 'oldGet': oldGet, 'logged_in': logged_in, 'listings': listings, 'order': order, 'list_title': list_title})
    
