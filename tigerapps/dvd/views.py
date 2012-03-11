from django.shortcuts import get_object_or_404, render_to_response
from dvd.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.template import RequestContext, loader
from django_cas.decorators import user_passes_test
from django.contrib.auth.models import User
from dvd.emails import *
from django.http import HttpResponse
from dsml import *
import datetime

def home(request):
    DVD_list = DVD.objects.all().order_by('sortname')
    return render_to_response('dvd/index.html', {'DVD_list': DVD_list})

@login_required
@user_passes_test(lambda u: u.is_staff)
def outstanding(request):
    rentalList = Rental.objects.filter(dateReturned=None).order_by('dateDue').reverse()
    return render_to_response('dvd/outstanding.html', {'rentalList': rentalList})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
<<<<<<< HEAD
def checkout(request, choice):
=======
def checkout(request):
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
    return render_to_response('dvd/checkout.html')
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def checkin_user(request):
    if 'netid' not in request.GET:
        return render_to_response('dvd/checkin.html')
    
    netid = request.GET['netid']
    
    user_info = gdi(netid)
    
    rentalList = Rental.objects.filter(netid=netid).filter(dateReturned=None).order_by('dateDue').reverse()
    return render_to_response('dvd/user.html', {'netid': netid, 'user_info': user_info, 'rentalList': rentalList})

@login_required
@user_passes_test(lambda u: u.is_staff)
def checkin_choices(request):
    return render_to_response('dvd/checkin_choices.html')
    
def ambiguous(request):
    ambiguous_list = DVD.objects.all()
    return render_to_response('dvd/ambiguous.html', {'ambiguous_list': ambiguous_list})

@login_required
@user_passes_test(lambda u: u.is_staff)
def checkin_dvd(request):
    #rental_list = Rental.objects.filter(dateReturned=None)
    
    if request.method == "POST" and 'dvd' in request.POST:
<<<<<<< HEAD
        dvd_list = request.POST.getlist('dvd')
=======
        dvd_list = request.POST.getlist('dvd') #list of dvd's checked
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
        ambiguous_list = [] # When more than one copy is checked out
        checked_list = []
        for dvd_id in dvd_list:
            dvd = DVD.objects.get(pk=dvd_id)
            dvd.amountLeft += 1
<<<<<<< HEAD
            #dvd.save()
            
            if dvd.amountTotal - dvd.amountLeft > 1:
                ambiguous_list.append(dvd)
=======
            dvd.save()
            
            #if there's copies of dvd_id still checked out
            if dvd.amountTotal - dvd.amountLeft > 1:
                ambiguous_list.append(dvd)
            #if all of the copies of dvd_id are checked in
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
            else:
                checked_list.append(dvd)
                rental_list = Rental.objects.filter(dateReturned=None, dvd=dvd)
                for rental in rental_list:
                    rental.dateReturned = datetime.datetime.now()
<<<<<<< HEAD
                    #rental.save()
=======
                    rental.save()
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
                
        if len(ambiguous_list) == 0:
            confirm = "The following DVDs have been checked in: " + str(checked_list)
            return render_to_response('dvd/confirm.html', {'title': "Success!", 'confirm': confirm})
        else:
<<<<<<< HEAD
=======
            #This allows the person checking in the dvd to select which copy was checked in
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
            return render_to_response('dvd/ambiguous.html', {'ambiguous_list': ambiguous_list, 'checked_list': checked_list})
    
    dvd_list = DVD.objects.all()
    excludes = []
    
    for dvd in dvd_list:
        if dvd.amountLeft == dvd.amountTotal:
            excludes.append(dvd.pk)

    dvd_list = dvd_list.exclude(pk__in=excludes).order_by('sortname')
    return render_to_response('dvd/checkindvd.html', {'dvd_list': dvd_list})
   
    '''
    error = False
    dvdNames = []
    errorDVD = []
    checklist = request.POST.getlist('rental')

    for pk in checklist:
        rental = Rental.objects.get(rentalID=int(pk))
        rental.dateReturned = datetime.datetime.now()
        rental.save()
        dvdNames.append(rental.dvd.name)

        if rental.dvd.amountLeft < rental.dvd.amountTotal:
            if rental.dvd.amountLeft == 0:
                noticeList = Notice.objects.filter(dvd=rental.dvd)
                sendNotice(noticeList, rental.dvd)

            rental.dvd.amountLeft += 1
            rental.dvd.save()
        else:
            error = True
            errorDVD.append(rental.dvd.name)

    if (error == False):
        return render_to_response('dvd/checkindvd.html', {'dvdNames': dvdNames})
    else:
        error = "The following DVD's have already been checked in! (Don't worry, the system already considers it returned)"
        return render_to_response('dvd/error.html', {'error': error, 'errorDVD': errorDVD})
    '''
@login_required
@user_passes_test(lambda u: u.is_staff)
def checkin_dvdlist(request):
<<<<<<< HEAD
=======
    #2/28/2012: Doesn't work, purpose unclear
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
    dvdList = DVD.objects.filter(amountLeft__lt=amountTotal)

    return render_to_response('dvd/checkindvd.html', {'dvdList': dvdList})
  
@login_required
@user_passes_test(lambda u: u.is_staff)
def checkout_user(request):
    netid = request.GET['netid']
    
    user_info = gdi(netid)
    if user_info is None:
        return render_to_response('dvd/user_not_found.html')
        
    warningList = Rental.objects.filter(netid=netid).filter(dateReturned=None).order_by('dateDue')
    DVD_list = DVD.objects.all().exclude(amountLeft=0).order_by('name')
    return render_to_response('dvd/checkoutuser.html', {'netid': netid, 'DVD_list': DVD_list, 'warningList': warningList})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def checkout_dvd(request):
    netid = request.POST['netid']
    
    user_info = gdi(netid)
    if user_info is None:
        return render_to_response('dvd/user_not_found.html')
        
    due = request.POST['due']
    checklist = request.POST.getlist('dvd')
    now = datetime.datetime.now()
    dvdNames = []
    
    for pk in checklist:
        dvd = DVD.objects.get(dvd_id=int(pk))
        dvd.amountLeft -= 1
        dvd.save()
        rental = Rental(netid=netid, dvd=dvd, dateRented=now, dateDue=(now + datetime.timedelta(days=int(due))), dateReturned=None)
        rental.save()
        dvdNames.append(dvd.name)
    
    return render_to_response('dvd/checkoutdvd.html', {'netid': netid, 'dvdNames': dvdNames})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin(request):
    return render_to_response('dvd/admin.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit(request):
    DVD_list = DVD.objects.all().order_by('name')
    return render_to_response('dvd/edit.html', {'DVD_list': DVD_list})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def editdvd(request, dvd_id):
    dvd = get_object_or_404(DVD, pk=dvd_id)
    change = False
    if (request.method == 'POST'):
        dvd = get_object_or_404(DVD, pk=dvd_id)
        dvd.name = request.POST['name']
        dvd.sortname = request.POST['sortname']
        dvd.amountTotal = request.POST['amountTotal']
        dvd.amountLeft = request.POST['amountLeft']
        dvd.imdbID = request.POST['imdbID']
        dvd.save()
        change = True
    return render_to_response('dvd/editdvd.html', {'dvd': dvd, 'change': change})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def adddvd(request):
    previous = None
    if (request.method == 'POST'):
        name = request.POST['name']
        sortname = request.POST['sortname']
        amountTotal = request.POST['amountTotal']
        amountLeft = request.POST['amountLeft']
        imdbID = request.POST['imdbID']
        previous = DVD(name=name, sortname=sortname, amountTotal=amountTotal, timesRented=0, amountLeft=amountLeft, imdbID=imdbID)
        previous.save()
    return render_to_response('dvd/adddvd.html', {'previous': previous})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete(request, dvd_id):
    dvd = get_object_or_404(DVD, pk=dvd_id)
    dvdname = dvd.name
    rentalList = Rental.objects.filter(dvd = dvd)
    for rental in rentalList:
        rental.delete()
    dvd.delete()
    return render_to_response('dvd/delete.html', {'dvdname': dvdname})
        
@login_required
@user_passes_test(lambda u: u.is_staff)
def adduser(request):
    if (request.method == 'POST'):
        netid = request.POST['netid']
        
        user_info = gdi(netid)
        if user_info is None:
            return render_to_response('dvd/user_not_found.html')
            

        try:
            user = User.objects.get(username=netid)
        except User.DoesNotExist:
            user = User(username=netid, password="") #Password doesn't matter with CAS!
        user.is_staff = True 
        user.save()
    return render_to_response('dvd/adduser.html')
    
def forbidden(request, template_name='403.html'):
    """Default 403 handler"""
    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))
    
@login_required
def notify(request, dvd_id):
    dvd = DVD.objects.get(dvd_id=dvd_id)
    try:
        notice = Notice.objects.filter(netid=request.user.username).get(dvd=dvd)
        title = "Ruh-roh!"
        confirm = "You're already going to be notified when a copy of " + dvd.name + " comes by. Hold your horses!"
    except:
        notice = Notice(netid=request.user.username, dvd=dvd)
        notice.save()
        title = "Success!"
        confirm = "You will get an email as soon as a copy of " + dvd.name + " is available"
    
    return render_to_response('dvd/confirm.html', {'title': title, 'confirm': confirm})
    
