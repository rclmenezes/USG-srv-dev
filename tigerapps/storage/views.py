import uuid
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django_cas.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from paypal.standard.forms import PayPalPaymentsForm
from utils import paypal
from storage.forms import RegistrationForm
from storage.models import *


def home(request):
    postList = Post.objects.all().order_by('posted').reverse()
    paginator = Paginator(postList, 3)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page # is out of range, deliver 1st page of results.
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(1)
        
    return render_to_response('storage/index.html', 
                              {'posts': posts},
                              RequestContext(request))

@login_required
def register(request):
    dp_qset = DropoffPickupTime.objects.all()
    dp_times = {(x.id, (x.dropoff_time.strftime("%a %m/%d/%Y %I:%M%p"),
                x.pickup_time.strftime("%a %m/%d/%Y %I:%M%p"),
                x.n_boxes_total-x.n_boxes_bought)) for x in dp_qset} 
    
    if request.method == 'POST':
        reg_form = RegistrationForm(request.POST)
        if not reg_form.is_valid():
            return render_to_response('storage/register.html',
                                      {'reg_form': reg_form,
                                       'box_price': reg_form.BOX_PRICE,
                                       'max_boxes': reg_form.MAX_BOXES,
                                       'reg_form_dptime_choice': request.POST['dropoff_pickup_time'],
                                       'dp_times': dp_times},
                                      RequestContext(request))
        reg_form.save(request.user, commit=True)
        pp_details = {
            'amount': float(box_price),
            'item_name': "USG summer storage boxes",
            'item_number': "box",
            'quantity': pp_quantity,
            
            'invoice': str(uuid.uuid1()), #PayPal wants a unique invoice ID 
            'return_url': settings.SITE_DOMAIN,
            'cancel_return': settings.SITE_DOMAIN,
        }
        pp_form = PayPalPaymentsForm(initial=pp_details)
        if settings.DEBUG:
            pp_form_rendered = form.sandbox()
        else:
            pp_form_rendered = form.render()
        return render_to_response('storage/register_paypal.html')
        
    reg_form = RegistrationForm()
    
    return render_to_response('storage/register.html',
                              {'reg_form': reg_form,
                               'box_price': reg_form.BOX_PRICE,
                               'max_boxes': reg_form.MAX_BOXES,
                               'dp_times': dp_times},
                              RequestContext(request))
