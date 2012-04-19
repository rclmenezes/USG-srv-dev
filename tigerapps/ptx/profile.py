# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.http import QueryDict
from django import forms
from django.db.models import Q
from ptx.models import User, Offer, Request, Book
from ptx.ptxrender import render_to_response

from django.contrib.formtools.wizard import FormWizard
from django.core.exceptions import PermissionDenied
from datetime import date

class CompleteUserForm(forms.ModelForm):
    """Represents a form for editing a user profile's basic
    information."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'dorm_name', 'dorm_room')

def render_form(form, request, message=u''):
    return render_to_response(request, 'ptx/profile.html',
                              dict(form=form, message=message))

def profile(request):
    if not request.user.is_authenticated():
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'Complete User Profile',
                                   'redirect_url': '/profile'} )

    if request.method == 'POST':
        form = CompleteUserForm(request.POST)
        if form.is_valid():
            # break down the course input
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            dorm_name = form.cleaned_data['dorm_name']
            dorm_room = form.cleaned_data['dorm_room']

            user, created = User.objects.get_or_create(net_id=request.user.username)
            if first_name != '':
                user.first_name = first_name
            if last_name != '':
                user.last_name = last_name
            if dorm_name != '':
                user.dorm_name = dorm_name
            if dorm_room != '':
                user.dorm_room = dorm_room

            user.save()

        return HttpResponseRedirect('/account')

    else:
        message = u''
        if request.GET.get("n") == "true":
            message = u"This is your first time logging in. Please fill out this basic information that will be used to contact you. It will only be shared with people who buy your books and the people that you buy from."
        user, created = User.objects.get_or_create(net_id=request.user.username)
        form = CompleteUserForm(instance=user)
        return render_form(form, request, message)

def myaccount(request):
    if not request.user.is_authenticated():
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'My PTX Account',
                                   'redirect_url': '/account'} )

    # one of these must be set to true somewhere.
    clickid = 1
    if request.method == 'GET':
        tabid = request.GET.get("t")
        if tabid == "basicinfo":
            clickid = 1
        elif tabid == "pending":
            clickid = 3

    today = date.today()
    user, created = User.objects.get_or_create(net_id=request.user.username)

    # has this user posted a change to his account
    if request.method == 'POST':
        q = request.POST
        if "delete_open" in q:
            # user remove an open offer
            offerid = q["open_offerid"]
            offers = Q(id=offerid) & Q(user__net_id=user.net_id)
            offers = Offer.objects.filter(offers)
            if len(offers) > 0:
                offer = offers[0]
                offer.delete()

        elif "edit_open" in q:
            # user wants to edit an offer.
            offerid = q["open_offerid"]
            return HttpResponseRedirect("/editoffer/" + offerid)

        elif "pending_closed" in q:
            # user closed a pending offer
            offerid = q["pending_offerid"]
            offers = Q(id=offerid) & Q(user__net_id=user.net_id)
            offers = Offer.objects.filter(offers)
            if len(offers) > 0:
                offer = offers[0]
                offer.status = 'c'
                offer.date_closed = today
                offer.save()
                # record this in the user's dollars earned.
                earned = user.dollars_earned
                user.dollars_earned = earned + offer.price
                user.save()

            clickid = 3

        elif "pending_opened" in q:
            # user reopened a pending offer
            offerid = q["pending_offerid"]
            offers = Q(id=offerid) & Q(user__net_id=user.net_id)
            offers = Offer.objects.filter(offers)
            if len(offers) > 0:
                offer = offers[0]
                offer.status = 'o'
                offer.save()

            clickid = 3

        elif "pending_req_closed" in q:
            # user closed a pending request
            requestid = q["pending_requestid"]
            offers = Q(id=requestid) & Q(user__net_id=user.net_id)
            requests = Request.objects.filter(offers)
            if len(requests) > 0:
                req = requests[0]
                req.status = 'c'
                req.date_closed = today
                req.save()
                # record this in dollars spent
                spent = user.dollars_spent
                user.dollars_spent = spent + req.maxprice
                user.save()

            clickid = 3

        elif "pending_req_opened" in q:
            # user put request back onto wish list
            requestid = q["pending_requestid"]
            offers = Q(id=requestid) & Q(user__net_id=user.net_id)
            requests = Request.objects.filter(offers)
            if len(requests) > 0:
                req = requests[0]
                req.status = 'o'
                req.save()

            clickid = 3

        elif "delete_req" in q:
            # user deleted a request
            requestid = q["request_id"]
            offers = Q(id=requestid) & Q(user__net_id=user.net_id)
            reqs = Request.objects.filter(offers)
            if len(reqs) > 0:
                req = reqs[0]
                req.delete()

        elif "rate_buyer_up" in q:
            # user rated buyer thumbs up
            clickid = 3
            if "rater_pending_offer_id" in q:
                offerid = q["rater_pending_offer_id"]
            else:
                offerid = q["rater_offer_id"]

            offer = Offer.objects.get(id=offerid)
            if offer != None:
                offer.rate_buyer(1, user.net_id)

        elif "rate_buyer_down" in q:
            # user rated buyer thumbs down
            clickid = 3
            if "rater_pending_offer_id" in q:
                offerid = q["rater_pending_offer_id"]
            else:
                offerid = q["rater_offer_id"]
            offer = Offer.objects.get(id=offerid)
            if offer != None:
                offer.rate_buyer(-1, user.net_id)

        elif "rate_seller_up" in q:
            # user rated seller thumbs up
            clickid = 3
            if "rater_pending_request_id" in q:
                requestid = q["rater_pending_request_id"]
            else:
                requestid = q["rater_request_id"]
            req = Request.objects.get(id=requestid)
            if req != None:
                if not req.has_rated:
                    offer = req.offer
                    offer.rate_seller(1, user.net_id)

        elif "rate_seller_down" in q:
            # user rated seller thumbs down
            clickid = 3
            if "rater_pending_request_id" in q:
                requestid = q["rater_pending_request_id"]
            else:
                requestid = q["rater_request_id"]
            req = Request.objects.get(id=requestid)
            if req != None:
                if not req.has_rated:
                    offer = req.offer
                    offer.rate_seller(-1, user.net_id)

    request_list = \
        Request.objects.filter(Q(user__net_id=user.net_id) &
                               Q(status='o')).order_by('date_open')

    pending_requests = \
        Q(user__net_id=user.net_id) & \
        (Q(status='p') \
         | Q(offer__status='p') \
         | Q(has_rated=False) \
         | Q(offer__has_rated=False))
    pending_requests = \
        Request.objects.filter(pending_requests).order_by('date_pending')

    completed_requests = \
        Q(user__net_id=user.net_id) & \
        Q(status='c') & \
        Q(offer__status='c') & \
        Q(has_rated=True) & \
        Q(offer__has_rated=True)

    completed_requests = \
        Request.objects.filter(completed_requests).order_by('date_closed')
    open_offers = \
        Offer.objects.filter(Q(status='o') &
                             Q(user__net_id=user.net_id)).order_by('date_open')

    pending_offers = \
        Offer.objects.filter(Q(status='p') &
                             Q(user__net_id=user.net_id)).order_by('date_pending')

    completed_offers = \
        Offer.objects.filter(Q(status='c') &
                             Q(user__net_id=user.net_id)).order_by('date_closed')

    has_open = len(open_offers) > 0
    has_pending = len(pending_offers) > 0
    # Pending and completed offers are slightly more nuanced than
    # status="p" it seems. Consult Offer.is_pending in ptx.models
    # for more details.
    has_pending = has_pending or any(o.is_pending() for o in completed_offers)
    has_completed = not all(o.is_pending() for o in completed_offers)
    has_requests = len(request_list) > 0
    has_pending_reqs = len(pending_requests) > 0
    has_completed_reqs = len(completed_requests) > 0

    dict = {'user_data': user,
            'request_list': request_list,
            'open_offers': open_offers,
            'pending_offers': pending_offers,
            'completed_offers': completed_offers,
            'pending_requests': pending_requests,
            'completed_requests': completed_requests,
            'has_open_offers': has_open,
            'has_pending_offers': has_pending,
            'has_completed_offers': has_completed,
            'has_requests': has_requests,
            'has_pending_reqs': has_pending_reqs,
            'has_completed_reqs': has_completed_reqs,
            'clickid': clickid,
            }

    return render_to_response(request, 'ptx/myaccount.html', dict)
