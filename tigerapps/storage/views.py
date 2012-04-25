import sys, os
import uuid
from os import path
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django_cas.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from paypal.standard.forms import PayPalPaymentsForm
from utils import paypal
from paypal import standard
from paypal.standard import ipn
from storage.forms import *
from storage.models import *
from django.core.mail import send_mail

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
    #Make sure user didn't already register
    #Make sure user didn't already register
    try:    
        status = UnpaidOrder.objects.get(user=request.user)
        return redirect('storage/status.html')
    except:
        pass
    
    #Get the list of dropoffpickuptimes
    dp_qset = DropoffPickupTime.objects.all()
    dp_times = [(str(x.id), x.dropoff_time.strftime("%a %m/%d/%Y %I:%M%p"),
                x.pickup_time.strftime("%a %m/%d/%Y %I:%M%p"),
                x.n_boxes_total-x.n_boxes_bought) for x in dp_qset]
    
    #Process the user's input if POST
    if request.method == 'POST':
        reg_form = RegistrationForm(request.POST)
        if not reg_form.is_valid():
            try:    c = request.POST['dropoff_pickup_time']
            except: c = None
            return render_to_response('storage/register_1_info.html',
                                      {'reg_form': reg_form,
                                       'box_price': reg_form.BOX_PRICE,
                                       'max_boxes': reg_form.MAX_BOXES,
                                       'dp_choice': c,
                                       'dp_times': dp_times},
                                      RequestContext(request))
        reg_form.save(request.user, commit=True)
        
        #Render data to show on next page
        status = UnpaidOrder.objects.get(user=request.user)
        reg_info = ((0, 'NetID:', request.user.username),
                    (0, 'Email:', request.user.username+'@princeton.edu'),
                    (0, 'Cell phone number*:', status.cell_number),
                    (1, 'Dropoff/pickup time*:', str(status.dropoff_pickup_time).split(', ')),
                    (0, 'Price per box:', '$'+reg_form.BOX_PRICE),
                    (0, 'Quantity (max %d)*:'%reg_form.MAX_BOXES, status.n_boxes_bought),
                    (0, 'Total price:', '$%.2f'%(float(reg_form.BOX_PRICE)*status.n_boxes_bought)),
                    (0, ' ', ' '),
                    (0, 'Proxy name:', status.proxy_name),
                    (0, 'Proxy email:', status.proxy_email))
        pp_details = {
            'business': 'it@princetonusg.com',
            'item_name': "USG summer storage boxes",
            'item_number': "box",
            'amount': reg_form.BOX_PRICE,
            'quantity': status.n_boxes_bought,
            
            'invoice': str(uuid.uuid1()), #PayPal wants a unique invoice ID 
            'notify_url': 'http://dev.storage.tigerapps.org/paypal/ipntesturl123/',
            'return_url': 'http://dev.storage.tigerapps.org/register/complete/',
            'cancel_return': settings.SITE_DOMAIN+'/register/',
        }
        pp_form = PayPalPaymentsForm(initial=pp_details)
        pp_form_rendered = pp_form.sandbox()
        #pp_form_rendered = pp_form.render()
        return render_to_response('storage/register_2_paypal.html',
                                  {'reg_info': reg_info,
                                   'pp_info': pp_form_rendered},
                                  RequestContext(request))
    
    #Return empty form if GET
    reg_form = RegistrationForm()
    return render_to_response('storage/register_1_info.html',
                              {'reg_form': reg_form,
                               'box_price': reg_form.BOX_PRICE,
                               'max_boxes': reg_form.MAX_BOXES,
                               'dp_times': dp_times},
                              RequestContext(request))

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from paypal import standard
from paypal.standard import ipn
from paypal.standard.ipn import views

def my_ipn(request):
    try :
        toReturn = ipn.views.ipn(request)
        return toReturn
    except Exception as e:
        s = str(e)
        try:
            s += str(sys.exc_info()[2].tb_lineno)
            fname = os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1]  
            s += '\n' + fname
        except Exception as e2:
            s += '\n' + str(e2) + '\n'
        send_mail('Subject here', s, 'from@example.com',
              ['it@princetonusg.com'], fail_silently=False)
        return HttpResponse('OKAY')

@login_required
def register_complete(request):
    return render_to_response('storage/register_3_complete.html',
                              {},
                              RequestContext(request))

@login_required
def status(request):
    try:
        status = UnpaidOrder.objects.get(user=request.user)
    except:
        return render_to_response('storage/status.html',
                                  {},
                                  RequestContext(request))

    reg_info = ((0, 'NetID:', request.user.username),
                (0, 'Email:', request.user.username+'@princeton.edu'),
                (0, 'Cell phone number:', status.cell_number),
                (1, 'Dropoff/pickup time:', str(status.dropoff_pickup_time).split(', ')),
                (0, 'Price per box:', '$'+RegistrationForm.BOX_PRICE),
                (0, 'Quantity:', status.n_boxes_bought),
                (0, 'Total paid:', '$%.2f'%(float(RegistrationForm.BOX_PRICE)*status.n_boxes_bought)))
    proxy_info = (status.proxy_name, status.proxy_email)
    
    if request.method == 'POST':
        form = ProxyUpdateForm(request.POST)
        if form.is_valid():
            form.save(status)
    form = ProxyUpdateForm()
    
    return render_to_response('storage/status.html',
                              {'reg_info': reg_info,
                               'proxy_info': proxy_info,
                               'proxy_form': form},
                              RequestContext(request))

