# mships.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for group membership settings

from globalsettings import SITE_URL,SITE_EMAIL,EMAIL_HEADER_PREFIX
from email_msg import *
from django.core.mail import send_mail
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from models import *
from views import *
from forms import *

def settings(request, group):
    """Set/change membership settings."""

    login_check(request)
    try:
        g = Group.objects.get(url__exact=group)
        mship = Membership.objects.get(group=g,student__exact=request.session['user'])
    except:
        return redirect_index(request)

    # Process form
    err_msg = ''
    confirm_msg = ''
    if request.method == "POST":
        if 'remove' in request.POST:
            # Remove member from group
            if mship.mship_notifications:
                send_mail(EMAIL_HEADER_PREFIX+'You Have Left \"%s\"'%g.name, MSHIP_LEAVE_EMAIL % g.name, SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
            mship.delete()
            return redirect('/groups/%s/'%group)
        elif 'resign_to_member' in request.POST:
            # change from officer to member
            mship.type = 'M'
            mship.save()
            if mship.mship_notifications:
                send_mail(EMAIL_HEADER_PREFIX+'Status Change in \"%s\"'%g.name, MSHIP_STATUS_CHANGE_EMAIL % (g.name, 'Officer','Member'), SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
            confirm_msg = 'You are now a normal member of this group.'
            form = MshipSettingsForm(instance=mship)
        elif 'resign_to_subscriber' in request.POST:
            # change from officer/member to subscriber
            if mship.type == 'O':
                old = 'Officer'
            else:
                old = 'Member'
            mship.type = 'S'
            mship.save()
            if mship.mship_notifications:
                send_mail(EMAIL_HEADER_PREFIX+'Status Change in \"%s\"'%g.name, MSHIP_STATUS_CHANGE_EMAIL % (g.name, old,'Subscriber'), SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
            confirm_msg = 'You are now a normal subscriber of this group.'
            form = MshipSettingsForm(instance=mship)
        else:
            # form data submitted
            form = MshipSettingsForm(request.POST, instance=mship)
            if form.is_valid():
                form.save()

                # Reconcile global/local notification settings
                s = request.session['user']
                if s.mship_notifications=='N' and form.cleaned_data['mship_notifications']==True:
                    s.mship_notifications = 'G'
                if s.mship_notifications=='Y' and form.cleaned_data['mship_notifications']==False:
                    s.mship_notifications = 'G'
                if s.feed_notifications=='N' and form.cleaned_data['feed_notifications']==True:
                    s.feed_notifications = 'G'
                if s.feed_notifications=='Y' and form.cleaned_data['feed_notifications']==False:
                    s.feed_notifications = 'G'
                if s.message_notifications=='N' and form.cleaned_data['message_notifications']==True:
                    s.message_notifications = 'G'
                if s.message_notifications=='Y' and form.cleaned_data['message_notifications']==False:
                    s.message_notifications = 'G'
                if s.request_notifications=='N' and form.cleaned_data['request_notifications']==True:
                    s.request_notifications = 'G'
                if s.request_notifications=='Y' and form.cleaned_data['request_notifications']==False:
                    s.request_notifications = 'G'
                s.save()
                request.session['user'] = s
                confirm_msg = "Your settings have been changed"
            else:
                err_msg = 'There were errors with the following fields: '
    else:
        # new form
        form = MshipSettingsForm(instance=mship)

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
    try:
        user_req = MembershipRequest.objects.get(group=g, student=request.session['user'])
    except:
        user_req = None

    return render_to_response('groups/settings.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'confirm_msg':confirm_msg,
                               'err_msg':err_msg,
                               'requests':requests.count(),
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'user_req': user_req,
                               'mship':mship})
    
