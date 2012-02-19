# Create your views here.

import textwrap
from datetime import date

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail as _send_mail
from django.db.models import Q
from django.http import QueryDict

from ptx.models import Offer, Book, Course, User, Request
from ptx.ptxrender import render_to_response as render

def send_mail(subject, msg, _from, to):
    msg = textwrap.fill(msg, 70)
    return _send_mail(subject, msg, _from, to)

def confirm(request):
    """Controller for both /buy/confirm/{id} and /buy/confirm URLs,
    hence the default value for offerid."""

    if not request.method == "POST":
        return HttpResponseRedirect('/')

    # All our attempts to get an ID failed. Assume the user is
    # malicious and redirect away.
    offerid = request.POST.get('offer_id')
    if not offerid or not offerid.isdigit():
        return HttpResponseRedirect('/browse')

    try:
        offer = Offer.objects.get(id=int(offerid))
    except Offer.DoesNotExist:
        # Terribly invalid offer ID, inconsistent with our code.
        return HttpResponseRedirect(u'/browse')

    data = dict(offer=offer)
    user = request.session.get('user_data')
    if not user:
        url  = u'/buy/confirm'
        data = dict(header_text=u'Buy a book', redirect_url=url)
        return render(request, 'ptx/needlogin.html', data)

    # make sure that the offer is open
    if offer.status != 'o':
        # this shouldn't happen. TODO: do something reasonable
        return render(request, "ptx/alreadybought.html", data)

    # make sure that the user isn't trying to buy his own book.
    if offer.user == user:
        return render(request, "ptx/yourownbook.html", data)

    return render(request, 'ptx/confirmbuy.html', data)

def buy(request):
    """Controller for /buy. Inputs: user session, an offer ID.
    Outputs: a pending offer, a pending request, confirmation emails,
    and capitalism."""

    buyer = request.session.get('user_data')
    if not buyer:
        return render(request, 'ptx/needlogin.html',
                                  {'header_text': 'Buy a book',
                                   'redirect_url': '/'} )

    if not request.method == "POST":
        return HttpResponseRedirect('/')

    offerid = request.POST.get("offer_id")
    if not offerid or not offerid.isdigit():
        raise PermissionDenied()

    try:
        offer = Offer.objects.get(id=int(offerid))
    except Offer.DoesNotExist:
        # Terribly invalid offer ID, inconsistent with our code.
        return HttpResponseRedirect(u'/browse')

    data  = dict(offer=offer)
    today = date.today()

    # Offers must be open.
    if offer.status != 'o':
        # this shouldn't happen. TODO: do something reasonable
        return render(request, "ptx/alreadybought.html", data)

    # Prevent a person from buying his own book.
    if offer.user == buyer:
        return render(request, "ptx/yourownbook.html", data)

    # Change offer to pending.
    offer.status = 'p'
    offer.date_pending = today
    offer.save()

    # Give the buyer a pending request.
    buyer = request.session['user_data']

    # Check if a request exists already.
    requests = Request.objects.filter(Q(user=buyer)
                                      & Q(status='o')
                                      & Q(book=offer.book))
    if len(requests) > 0:
        # Update the request instead.
        req = requests[0]
        req.maxprice = offer.price
        req.date_pending = today
        req.status = 'p'
        req.offer = offer
        req.save()
    else:
        # Otherwise, create a new pending request.
        req = Request(user=buyer, book=offer.book, status='p',
                  maxprice=offer.price, date_open=today,
                  date_pending=today, offer=offer)
        req.save()

    seller = offer.user

    # Email the seller. ####################
    emailto = [seller.net_id + u"@princeton.edu"]
    emailsubject = u"PTX: Your book has been purchased!"
    emailfrom = u"ptx@princeton.edu"

    buyerclause = u"The buyer"
    if len(buyer.first_name) > 0 and len(buyer.last_name) > 0:
        args = buyer.first_name, buyer.last_name
        buyerclause = u"The buyer, %s %s," % args

    buyerdorm = u""
    if len(buyer.dorm_name) > 0 and len(buyer.dorm_room) > 0:
        args = buyer.dorm_name, buyer.dorm_room
        buyerdorm = u"The buyer lives in %s %s. " % args

    args = offer.book.title, offer.price, buyerclause, buyer.net_id, buyerdorm
    emailmessage = u"""\
Your book "%s" has just been purchased for $%s. %s can be reached at \
<%s@princeton.edu>. %sPlease contact him or her and complete the \
transaction. Please do not reply to this email; our robots disdain \
communication with humans.""" % args
    send_mail(emailsubject, emailmessage, emailfrom, emailto)

    # Email the buyer. ####################
    emailto = [buyer.net_id + u"@princeton.edu"]
    emailsubject = u"PTX: You purchased a book!"
    emailfrom = u"ptx@princeton.edu"

    sellerclause = u"The seller "
    if len(seller.first_name) > 0 and len(seller.last_name) > 0:
        args = seller.first_name, seller.last_name
        sellerclause = u"The seller, %s %s," % args

    sellerdorm = u""
    if len(seller.dorm_name) > 0 and len(seller.dorm_room) > 0:
        args = seller.dorm_name, seller.dorm_room
        sellerdorm = u"The seller lives in %s %s. " % args

    args = offer.book.title, offer.price, sellerclause, seller.net_id, sellerdorm
    emailmessage = u"""\
You just purchased "%s" for $%s. %s can be reached at \
<%s@princeton.edu>. %sPlease contact him or her and complete the \
transaction. Please do not reply to this email; our robots have little \
training in the inferior language of "English".""" % args
    send_mail(emailsubject, emailmessage, emailfrom, emailto)

    # Thank you page. ####################
    return render(request, 'ptx/buy.html', data)

