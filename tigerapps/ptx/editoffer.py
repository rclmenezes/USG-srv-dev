from django.http import HttpResponse, HttpResponseRedirect
from django.http import QueryDict
from django import forms
from django.db.models import Q
from django.contrib.formtools.wizard import FormWizard
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe

from ptx.ptxrender import render_to_response
from ptx.models import Offer, Book, Course, User
from ptx.ptxlogin import logged_in, getlogstatus

import re

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('price', 'desc')

def render(request, offer, form_data=None):
    if form_data == None:
        form = OfferForm(instance=offer)
    else:
        form = OfferForm(form_data)
    
    return render_to_response(request, 'ptx/editoffer.html', {
        'message': offer.user.net_id, 
        'book': offer.book,
        'offer_id': offer.pk,
        'form': form})

def editoffer(request, offer_id=None):
    # Can't do this unless logged in
    if not logged_in(request):
        return render_to_response(request, 'ptx/needlogin.html',
                                  {'header_text': 'Edit Your Offer',
                                   'redirect_url': '/editoffer/' + offer_id} )

    # see if the offer exists
    try:
        offer = Offer.objects.get(pk=offer_id)
    except Offer.DoesNotExist:
        raise PermissionDenied

    # see if the offer really belongs to the logged-in user
    if offer.user.net_id != request.session['user_data'].net_id:
        raise PermissionDenied

    if request.method == 'POST':
        form = OfferForm(request.POST)

        if form.is_valid():
            offer.desc = form.cleaned_data['desc']
            offer.price = form.cleaned_data['price']
            offer.save()

            return HttpResponseRedirect('/account')

        else:
            return render(request, offer, request.POST)

    elif request.method == 'GET':
        return render(request, offer)
    else:
        raise PermissionDenied


