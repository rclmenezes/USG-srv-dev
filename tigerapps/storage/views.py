import uuid
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from storage.models import Product

def product_detail(request):
    product = Product()
    product.title = "Box"
    product.price = 4
    paypal = {
        'amount': 6,
        'item_name': "Box",
        'item_number': "box",
        
        # PayPal wants a unique invoice ID
        'invoice': str(uuid.uuid1()), 
        
        # It'll be a good idea to setup a SITE_DOMAIN inside settings
        # so you don't need to hardcode these values.
        'return_url': settings.SITE_DOMAIN,
        'cancel_return': settings.SITE_DOMAIN,
    }
    form = PayPalPaymentsForm(initial=paypal)
    if settings.DEBUG:
        rendered_form = form.sandbox()
    else:
        rendered_form = form.render()
    return render_to_response('storage/paypal.html', {
        'product' : product,
        'form' : rendered_form,
    }, RequestContext(request))

