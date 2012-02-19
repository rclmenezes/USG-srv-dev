from email_msg import *
from globalsettings import SITE_URL,EMAIL_HEADER_PREFIX,ADMIN_EMAILS,SITE_EMAIL
import random
import string
from views import *
from models import *
from forms import *

def renew(request, group):
    if not login_check(request):
        return redirect_index(request)

    try:
        g = Group.objects.get(url=group)
        if g.active_status != 'R':
            raise Exception()
    except:
        return redirect_index(request)

    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
        if user_mship.type != 'O':
            raise Exception
    except:
        return redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method=='POST':
        form = RenewGroupForm(request.POST, instance=g)
        if form.is_valid():
            form.save()
            g.active_status = 'A'
            g.save()
            confirm_msg = 'Your group activity status has been confirmed.  Thank you.'
        else:
            err_msg = 'There were errors in the following fields: '            
    else:
        form = RenewGroupForm(instance=g)

    officers = Membership.objects.filter(group=g, type='O')

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])

    return render_to_response('groups/renew.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'form':form,
                               'group':g,
                               'officers':officers,
                               'err_msg':err_msg,
                               'confirm_msg': confirm_msg,
                               'unread_messages':unread.count(),
                               'requests':requests.count(),
                               'reactivate_req':reactivate_req,
                               'user_mship':user_mship})

def reactivate(request, group):
    if not login_check(request):
        return redirect_index(request)

    try:
        g = Group.objects.get(url=group)
    except:
        return redirect_index(request)

    if g.active_status != 'I':
        return redirect('/groups/%s'%g.url)
    if GroupReactivationRequest.objects.filter(group=g).count():
        return redirect('/groups/%s/'%g.url)

    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
        if user_mship.type != 'O':
            raise Exception
    except:
        return redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method=='POST':
        form = ReactivateGroupForm(request.POST, instance=g)
        if form.is_valid():
            # update profile
            form.save()
            
            # Create request model
            ticket = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
            while GroupReactivationRequest.objects.filter(ticket=ticket).count():
                ticket = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
            req = GroupReactivationRequest(group=g,ticket=ticket,supplicant=request.session['user'],reason=form.cleaned_data['reason_for_reactivation'])
            req.save()

            # Email
            send_mail(EMAIL_HEADER_PREFIX+'Reactivation Request for \"%s\"'%g.name, GROUP_REACTIVATE_REQUEST_EMAIL % (g.name, g.description, req.reason, request.session['user'].email, req.ticket,), SITE_EMAIL, ADMIN_EMAILS, fail_silently=False)
            send_mail(EMAIL_HEADER_PREFIX+'Reactivation Request Submitted for \"%s\"'%g.name, GROUP_REACTIVATE_ACK_EMAIL % (g.name,), SITE_EMAIL, [request.session['user'].email], fail_silently=False)

            confirm_msg = 'Your reactivation request has been submitted'
        else:
            err_msg = 'There were errors in the following fields: '            
    else:
        form = ReactivateGroupForm(instance=g)

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])

    officers = Membership.objects.filter(group=g, type='O')

    return render_to_response('groups/reactivate.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'form':form,
                               'officers':officers,
                               'group':g,
                               'err_msg':err_msg,
                               'confirm_msg': confirm_msg,
                               'unread_messages':unread.count(),
                               'requests':requests.count(),
                               'reactivate_req':reactivate_req,
                               'user_mship':user_mship})

def reactivate_process(request, ticket):
    try:
        g = GroupReactivationRequest.objects.get(ticket=ticket)        
    except:
        return redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    done = False
    try:
        if request.method == 'POST':
            if 'confirm' in request.POST:
                # reactivate
                g.group.active_status = 'A'
                g.group.save()
                send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Profile Reactivated'%g.group.name, GROUP_REACTIVATE_ACCEPT_EMAIL % g.group.name, SITE_EMAIL, [g.supplicant.email], fail_silently=False)
                g.delete()
                confirm_msg = 'Group profile successfully reactivated'
            elif 'reject' in request.POST:
                # delete request
                send_mail(EMAIL_HEADER_PREFIX+'Reactivation Request Rejected for \"%s\"'%g.group.name, GROUP_REACTIVATE_REJECT_EMAIL % (g.group.name,), SITE_EMAIL, [g.supplicant.email], fail_silently=False)      
                g.delete()
                confirm_msg = 'Reactivation request rejected'
            done=True
    except Exception, e:
#        raise Exception(e)
        err_msg='Unable to process request. Contact site admin.'

    return render_to_response('groups/reactivation_process_complete.html',
                              {'user':request.session['user'],
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'done':done,
                               'request':g,
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})
