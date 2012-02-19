# account.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for personal, global accounts

from globalsettings import SITE_EMAIL,SITE_URL,EMAIL_HEADER_PREFIX
from email_msg import *
from django.core.mail import send_mail
from django.shortcuts import render_to_response, redirect
from models import *
from views import *
from forms import *
import random
import string

def groups(request):
    """Display user's group affiliations."""

    if not login_check(request):
        redirect_index(request)

    # Get various affiliations
    mships_off = Membership.objects.filter(student=request.session['user'], type='O')
    mships_mem = Membership.objects.filter(student=request.session['user'], type='M')
    mships_req = MembershipRequest.objects.filter(student=request.session['user'])
    mships_sub = Membership.objects.filter(student=request.session['user'], type='S')

    return render_to_response('groups/account_groups.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'mships_off':mships_off,
                               'mships_mem':mships_mem,
                               'mships_req':mships_req,
                               'mships_sub':mships_sub,
                               'alpha':request.session['alpha'],})

def manage(request):
    """Account settings form."""

    if not login_check(request):
        redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        #form submitted
        form = AccountForm(request.POST, instance=request.session['user'])
        if form.is_valid():
            form.save()
            request.session['user'] = Student.objects.get(netid=request.session['user'].netid)

            # reconcile global/local notification settings
            s = request.session['user']
            if form.cleaned_data['mship_notifications'] == 'N':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.mship_notifications=False
                    m.save()
                request.session['user'].mship_notifications='N'
            elif form.cleaned_data['mship_notifications'] == 'Y':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.mship_notifications=True
                    m.save()
                request.session['user'].mship_notifications='Y'
            else:
                request.session['user'].mship_notifications='G'
            if form.cleaned_data['feed_notifications'] == 'N':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.feed_notifications=False
                    m.save()
                request.session['user'].feed_notifications='N'
            elif form.cleaned_data['feed_notifications'] == 'Y':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.feed_notifications=True
                    m.save()
                request.session['user'].feed_notifications='Y'                
            else:
                request.session['user'].feed_notifications='G'
            if form.cleaned_data['message_notifications'] == 'N':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.message_notifications=False
                    m.save()
                request.session['user'].message_notifications='N'
            elif form.cleaned_data['message_notifications'] == 'Y':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.message_notifications=True
                    m.save()
                request.session['user'].message_notifications='Y'
            else:
                request.session['user'].message_notifications='G'
            if form.cleaned_data['request_notifications'] == 'N':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.request_notifications=False
                    m.save()
                request.session['user'].request_notifications='N'
            elif form.cleaned_data['request_notifications'] == 'Y':
                mships = Membership.objects.filter(student=s)
                for m in mships:
                    m.request_notifications=True
                    m.save()
                request.session['user'].request_notifications='Y'
            else:
                request.session['user'].request_notifications='G'
            request.session['user'].save()
            confirm_msg = 'Settings changed successfully'
        else:
            err_msg = 'There were errors with the following fields: '
    else:
        # new form
        form = AccountForm(instance=request.session['user'])

    return render_to_response('groups/account_manage.html',
                              {'user':request.session['user'],
                               'form':form,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})

def register_group(request):
    """Form to register new group profile."""

    if not login_check(request):
        redirect_index(request)
        
    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # create request object
        g = GroupRequest(supplicant=request.session['user'])
        
        # Random, unique ticket
        g.ticket = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))
        while GroupRequest.objects.filter(ticket=g.ticket).count():
            g.ticket = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))
            
        form = NewGroupForm(request.POST, instance=g)
        if form.is_valid():
            form.save()

            # notification to USG, supplicant
            send_mail(EMAIL_HEADER_PREFIX+'New Group Request', GROUP_REQUEST_EMAIL % (form.instance.name, form.instance.description, form.instance.supplicant.email, form.instance.ticket,), SITE_EMAIL, ADMIN_EMAILS, fail_silently=False)
            send_mail(EMAIL_HEADER_PREFIX+'New Group Request Submitted for \"%s\"'%form.instance.name, GROUP_REQUEST_ACK_EMAIL % (form.instance.name,), SITE_EMAIL, [form.instance.supplicant.email], fail_silently=False)
            confirm_msg = 'Your request has been submitted.  You will recieve an email when it has been processed.'

            # Reset form
            form = NewGroupForm()
        else:
            err_msg = 'There were errors with the following fields: '
    else:
        # new form
        form = NewGroupForm()

    return render_to_response('groups/account_newgroup.html',
                              {'user':request.session['user'],
                               'form':form,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})

def process(request, ticket):
    """Process a group request."""

    login_check(request)

    try:
        g = GroupRequest.objects.get(ticket=ticket)        
    except:
        return redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    done = False
    try:
        if request.method == 'POST':
            if 'confirm' in request.POST:
                # create new group
                new = g.make_group()
                send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Profile Created'%new.name, GROUP_REQUEST_ACCEPT_EMAIL % (new.name, new.url), SITE_EMAIL, [g.supplicant.email], fail_silently=False)
                g.delete()
                confirm_msg = 'Group profile created successfully'
            elif 'reject' in request.POST:
                # delete request
                send_mail(EMAIL_HEADER_PREFIX+'New Group Request Rejected for \"%s\"'%g.name, GROUP_REQUEST_REJECT_EMAIL % (g.name,), SITE_EMAIL, [g.supplicant.email], fail_silently=False)      
                g.delete()
                confirm_msg = 'Group request rejected'
            done=True
    except Exception, e:
#        raise Exception(e)
        err_msg='Unable to process request. Contact site admin.'

    return render_to_response('groups/account_newgroup_confirm.html',
                              {'user':request.session['user'],
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'done':done,
                               'request':g,
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})
