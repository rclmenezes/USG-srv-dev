"""
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.mail import send_mail
from storage.models import *
from storage.forms import *
from django_cas.decorators import login_required, user_passes_test
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.core.urlresolvers import reverse

def paypal(request):
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "1.00",
        "invoice": "unique-invoice-id",
        "notify_url": "%s%s" % (settings.SITE_NAME, reverse('paypal-ipn')),
        "return_url": "http://www.example.com/your-return-location/",
        "cancel_return": "http://www.example.com/your-cancel-location/",
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form.sandbox()}
    return render_to_response("storage/paypal.html", context)
"""

import uuid
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django_cas.decorators import login_required, user_passes_test
from paypal.standard.forms import PayPalPaymentsForm
from storage.forms import RegistrationForm
from storage.models import Product

@login_required
def register(request):
    if request.method == 'POST':
        status_form = RegistrationForm(request.POST)
        if status_form.is_valid():
            log = status_form.save(request.user, commit=True)
            return render_to_response('storage/registration_complete.html')
        
    status_form = RegistrationForm()
    netid = request.user
    return render_to_response('storage/register.html', {'registration_form': status_form, 'user_netid': netid})
  

def product_detail(request):
    product = get_object_or_404(Product, slug="abc")
    paypal = {
        'amount': product.price,
        'item_name': product.title,
        'item_number': product.slug,
        
        # PayPal wants a unique invoice ID
        'invoice': str(uuid.uuid1()), 
        
        # It'll be a good idea to setup a SITE_DOMAIN inside settings
        # so you don't need to hardcode these values.
        'return_url': settings.SITE_DOMAIN + reverse('return_url'),
        'cancel_return': settings.SITE_DOMAIN + reverse('cancel_url'),
    }
    form = PayPalPaymentsForm(initial=paypal)
    if settings.DEBUG:
        rendered_form = form.sandbox()
    else:
        rendered_form = form.render()
    return render_to_response('paypal.html', {
        'product' : product,
        'form' : rendered_form,
    }, RequestContext(request))

