# edit.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for officers to edit groups/members, post news, etc.

from django.core.paginator import Paginator
from globalsettings import SITE_URL,SITE_EMAIL,TABLE_ENTRIES_PER_PAGE,EMAIL_HEADER_PREFIX,FBOOK_URL
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from models import *
from views import *
from groups import *
from forms import *
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from email_msg import *
from django.core.mail import send_mail
from stdimage import StdImageField
from datetime import datetime

def edit_profile(request, group):
    """Displays a page where officers can edit the group profile info."""
    
    # validate user is officer of group
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # Create inline formset
    LinkFormSet = inlineformset_factory(Group, Link, extra=2)

    # process form data
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # last update is now
        g.last_update = datetime.now()
        g.save

        form = GroupProfileForm(request.POST, request.FILES,instance=g)
        link_formset = LinkFormSet(request.POST, request.FILES,instance=g)

        if form.is_valid() and link_formset.is_valid():
            form.save()
            link_formset.save()
            link_formset = LinkFormSet(instance=g) # to add more link fields
            confirm_msg = 'Changes saved successfully.'
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        form = GroupProfileForm(instance=g)
        link_formset = LinkFormSet(instance=g)

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/edit_profile.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'form':form,
                               'formset':link_formset,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})
                             
def approve_members(request, group):
    """Render page for approving membership requests."""

    # Validate user is officer of group
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)
    
    # Actions on members
    err_list = []
    approve_list = []
    reject_list = []
    if request.method == 'POST':
        # last update is now
        g.last_update = datetime.now()
        g.save

        if 'approve' in request.POST:
            for netid in request.POST:
                if netid != 'approve':
                    try:
                        # Create membership
                        mship = MembershipRequest.objects.get(group=g, student__netid=netid)
                        mship.make_member()

                        # notify
                        if mship.notify_me:
                            send_mail(EMAIL_HEADER_PREFIX+'Membership Request to \"%s\" Approved'%mship.group.name, MSHIP_REQUEST_ACCEPT_EMAIL % (mship.group.name,mship.group.url), SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
                        mship.delete()
                        approve_list.append(netid)
                    except:
                        err_list.append(netid)
        elif 'reject' in request.POST:
            for netid in request.POST:
                if netid != 'reject':
                    try:
                        # delete request
                        mship = MembershipRequest.objects.get(group=g, student__netid=netid)

                        # notify
                        if mship.notify_me:
                            send_mail(EMAIL_HEADER_PREFIX+'Membership Request to \"%s\" Denied'%mship.group.name, MSHIP_REQUEST_REJECT_EMAIL % mship.group.name, SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
                        mship.delete()
                        reject_list.append(netid)
                    except:
                        err_list.append(netid)

    # Confirmation/error message
    confirm_msg = ''
    err_msg = ''
    if approve_list:
        confirm_msg = confirm_msg + '%d requests successfully approved' % len(approve_list)
    if reject_list:
        confirm_msg = confirm_msg + '%d requests successfully rejected' % len(reject_list)
    if err_list:
        err_msg = err_msg + 'Error: unable to process requests for:'
        first_time = True
        for netid in err_list:
            if not first_time:
                err_msg = err_msg + ',%s'%netid
            else:
                err_msg = err_msg + '%s'%netid
                first_time = False

    # search information
    if request.method == 'GET':
        form = SearchApproveForm(request.GET)
        if form.is_valid():
            if 'f_name' in form.cleaned_data and form.cleaned_data['f_name']:
                f_name_query = form.cleaned_data['f_name']
            else:
                f_name_query = ''
            if 'l_name' in form.cleaned_data and form.cleaned_data['l_name']:
                l_name_query = form.cleaned_data['l_name']
            else:
                l_name_query = ''
            if 'netid' in form.cleaned_data and form.cleaned_data['netid']:
                netid_query = form.cleaned_data['netid']
            else:
                netid_query = ''
            if 'year' in form.cleaned_data and form.cleaned_data['year']:
                year_query = int(form.cleaned_data['year'])
            else:
                year_query = None
    else:
        form = SearchApproveForm()
        f_name_query = ''
        l_name_query = ''
        netid_query = ''
        year_query = None
        
    # sort table
    sort = 'name'
    order_by = 'student__last_name'
    if 'sort' in request.GET:
        if request.GET['sort'] == 'netid':
            order_by = 'student__netid'
        elif request.GET['sort'] == 'name':
            order_by = 'student__last_name'
        elif request.GET['sort'] == 'year':
            order_by = 'student__year'
        sort = request.GET['sort']

    # Lookup requests
    if year_query:
        mships = MembershipRequest.objects.filter(group=g,student__last_name__icontains=l_name_query,student__first_name__icontains=f_name_query,student__netid__icontains=netid_query,student__year__exact=year_query).order_by(order_by)
    else:
        mships = MembershipRequest.objects.filter(group=g,student__last_name__icontains=l_name_query,student__first_name__icontains=f_name_query,student__netid__icontains=netid_query).order_by(order_by)

    # Paginate requests
    p = Paginator(mships, TABLE_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        mships = page.object_list
    except:
        page = p.page(p.num_pages)
        mships = page.object_list

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
        
    return render_to_response('groups/approve.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'fbook':FBOOK_URL,
                               'sort':sort,
                               'form':form,
                               'mships':mships,
                               'p':p,
                               'page':page,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'requests':requests.count(),
                               'confirm_msg':confirm_msg,
                               'err_msg':err_msg,
                               'alpha':request.session['alpha'],})
                              
def edit_members(request, group):
    """Render page for editing member status."""
    
    # Validate user is officer of group
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    if 'renew' in request.GET or 'renew' in request.POST:
        renew = True
    else:
        renew = False
    if 'reactivate' in request.GET or 'reactivate' in request.POST:
        reactivate = True
    else:
        reactivate = False


    # Actions on members
    err_list = []
    promote_list = []
    demote_list = []
    remove_list = []
    remove_notify_list = []
    promote_notify_list = []
    promote_notify_title_list = []
    demote_notify_list = []
    PromoteFormSet = modelformset_factory(Membership,form=PromoteForm,extra=0)
    if request.method == 'POST':
        # last update is now
        g.last_update = datetime.now()
        g.save
        if 'remove' in request.POST:
            for netid in request.POST:
                if netid != 'remove':  # ignore name of submit field
                    try:
                        mship = Membership.objects.get(group=g, student__netid=netid)
                        mship_email = str(mship.student.email)
                        mship_notify = mship.mship_notifications
                        mship.delete()  #TODO: Subscriber instead?
                        remove_list.append(netid)
                        if mship_notify:
                            remove_notify_list.append(mship_email)
                    except:
                        err_list.append(netid)
        elif 'promote' in request.POST:
            formset = PromoteFormSet(queryset=Membership.objects.filter(student__netid__in=request.POST,group=g))
            if formset.forms:
                return render_to_response('groups/promote.html',
                                          {'user':request.session['user'],
                                           'categories':request.session['categories'],
                                           'renew':renew,
                                           'reactivate':reactivate,
                                           'group':g,
                                           'formset':formset,
                                           'alpha':request.session['alpha'],})
        elif 'demote' in request.POST:
            for netid in request.POST:
                if netid != 'demote':
                    try:
                        mship = Membership.objects.get(group=g, student__netid=netid)
                        mship.type='M'
                        mship.save()
                        demote_list.append(mship)
                        if mship.mship_notifications:
                            demote_notify_list.append(str(mship.student.email))
                    except:
                        err_list.append(netid)
        elif 'promote_submit' in request.POST:
            formset = PromoteFormSet(request.POST, request.FILES)
            if formset.is_valid():
                for form in formset.forms:                
                    if form.cleaned_data['promote']:
                        m = form.instance
                        m.type = 'O'
                        m.title = form.cleaned_data['title']
                        m.officer_order = form.cleaned_data['officer_order']
                        if m.student.request_notifications == 'G' or m.student.request_notifications == 'Y':
                            m.request_notifications = True
                        else:
                            m.request_notifications = False
                        m.save()
                        promote_list.append(m)
                        if m.mship_notifications:
                            if m.title:
                                promote_notify_title_list.append([str(m.student.email),m.title])
                            else:
                                promote_notify_list.append(str(m.student.email))


    # Confirmation/error message
    confirm_msg = ''
    err_msg = ''
    if remove_list:
        confirm_msg = confirm_msg + '%d members successfully removed' % len(remove_list)
    if promote_list:
        confirm_msg = confirm_msg + '%d members successfully promoted' % len(promote_list)
    if demote_list:
        confirm_msg = confirm_msg + '%d members successfully demoted' % len(demote_list)
    if err_list:
        err_msg = err_msg + 'Error: unable to process requests for:'
        first_time = True
        for netid in err_list:
            if not first_time:
                err_msg = err_msg + ',%s'%netid
            else:
                err_msg = err_msg + '%s'%netid
                first_time = False

    # notify members
    if promote_notify_list:
        send_mail(EMAIL_HEADER_PREFIX+'You Have Been Promoted to an Officer in \"%s\"' % g.name, MSHIP_PROMOTE_EMAIL % (request.session['user'].full_name,g.name,g.url), SITE_EMAIL, promote_notify_list, fail_silently=False)
    if promote_notify_title_list:
        for p in promote_notify_title_list:
            send_mail(EMAIL_HEADER_PREFIX+'You Have Been Promoted to an Officer in \"%s\"' % g.name, MSHIP_PROMOTE_TITLE_EMAIL % (request.session['user'].full_name,g.name,p[1],g.url), SITE_EMAIL, [p[0]], fail_silently=False)
    if demote_notify_list:
        send_mail(EMAIL_HEADER_PREFIX+'You Have Been Demoted in \"%s\"'%g.name, MSHIP_DEMOTE_EMAIL % g.name, SITE_EMAIL, demote_notify_list, fail_silently=False)
    if remove_notify_list:
        send_mail(EMAIL_HEADER_PREFIX+'You Have Been Removed From \"%s\"'%g.name, MSHIP_REMOVE_EMAIL % (g.name,g.url), SITE_EMAIL, remove_notify_list, fail_silently=False)

    # search information
    if request.method == 'GET':
        form = SearchMemberForm(request.GET)
        if form.is_valid():
            if 'f_name' in form.cleaned_data and form.cleaned_data['f_name']:
                f_name_query = form.cleaned_data['f_name']
            else:
                f_name_query = ''
            if 'l_name' in form.cleaned_data and form.cleaned_data['l_name']:
                l_name_query = form.cleaned_data['l_name']
            else:
                l_name_query = ''
            if 'netid' in form.cleaned_data and form.cleaned_data['netid']:
                netid_query = form.cleaned_data['netid']
            else:
                netid_query = ''
            if 'year' in form.cleaned_data and form.cleaned_data['year']:
                year_query = int(form.cleaned_data['year'])
            else:
                year_query = None
            if 'rank' in form.cleaned_data and form.cleaned_data['rank']:
                if form.cleaned_data['rank'] == 'O':
                    rank_query = ['O']
                elif form.cleaned_data['rank'] == 'M':
                    rank_query = ['M']
                else:
                    rank_query = ['O','M']
            else:
                rank_query = ['O','M']
    else:
        form = SearchMemberForm()
        f_name_query = ''
        l_name_query = ''
        netid_query = ''
        year_query = None
        rank_query = ['M','O']
    

    # Sort table
    order_by = 'rank'
    sort = 'rank'
    if 'sort' in request.GET:
        if request.GET['sort'] == 'netid':
            order_by = 'student__netid'
        elif request.GET['sort'] == 'name':
            order_by = 'student__last_name'
        elif request.GET['sort'] == 'year':
            order_by = 'student__year'
        elif request.GET['sort'] == 'rank':
            order_by = 'rank'
        sort = request.GET['sort']

    # Get from db
    if year_query:
        if order_by == 'rank':
            mships = Membership.objects.filter(group=g, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query,student__year__exact=year_query).order_by('-type','-has_order','officer_order').exclude(student=request.session['user'])
        else:
            mships = Membership.objects.filter(group=g, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query,student__year__exact=year_query).order_by(order_by).exclude(student=request.session['user'])
    else:
        if order_by == 'rank':
            mships = Membership.objects.filter(group=g, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query).order_by('-type','-has_order','officer_order').exclude(student=request.session['user'])
        else:
            mships = Membership.objects.filter(group=g, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query).order_by(order_by).exclude(student=request.session['user'])

    # Paginate
    p = Paginator(mships, TABLE_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        mships = page.object_list
    except:
        page = p.page(p.num_pages)
        mships = page.object_list

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
            user_mship = None

    return render_to_response('groups/edit_members.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'sort':sort,
                               'renew':renew,
                               'reactivate':reactivate,
                               'p':p,
                               'fbook':FBOOK_URL,
                               'page':page,
                               'form':form,
                               'mships':mships,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'requests':requests.count(),
                               'confirm_msg':confirm_msg,
                               'err_msg':err_msg,
                               'alpha':request.session['alpha'],})

def upload_image(request, group):
    """Form form uploading group image"""
    
    # validate user is officer of group
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # process form data
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # last update is now
        g.last_update = datetime.now()
        g.save

        form = ImageUploadForm(request.POST, request.FILES, instance=g)
        if form.is_valid():
            form.save()
            confirm_msg = 'Changes saved successfully.'
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        form = ImageUploadForm(instance=g)

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
    
    return render_to_response('image.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})

def handle_uploaded_file(f, g, l):
    path_str = '/home/atrippe/Student_Groups/media/Files/'+f.name
    destination = open(path_str, 'w')
    for chunk in f.chunks():
        destination.write(chunk)
    upload = GroupFile(group=g,filepath=path_str,label=l)
    upload.save()
    destination.close()
    
def files(request, group):
    """Upload/delete group files."""
    
    # validate user is officer of group
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # Create inline formset
    FileFormSet = inlineformset_factory(Group, GroupFile, extra=5, max_num=5)

    # process form data
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # last update is now
        g.last_update = datetime.now()
        g.save

        formset = FileFormSet(request.POST, request.FILES, instance=g)
        if formset.is_valid():
#            i = 0
#            for form in formset.forms:
#                if i == 5:
#                    break
#                try:
#                    handle_uploaded_file(request.FILES['groupfile_set-%d-file'%i], g, request.POST['groupfile_set-%d-label'%i])
#                except:
#                    pass
#                i = i + 1
            formset.save()
            confirm_msg = 'Changes saved successfully.'
        else:
            err_msg = 'There were errors in the following fields: '

    formset = FileFormSet(instance=g)

    # Pass outstanding requests, mship info for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
    
    return render_to_response('upload_files.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'formset':formset,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})
    
