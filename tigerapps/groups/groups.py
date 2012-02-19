# groups.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for browsing groups

from django.core.paginator import Paginator
from globalsettings import SITE_URL,SITE_EMAIL,TABLE_ENTRIES_PER_PAGE,SEARCH_ENTRIES_PER_PAGE,EMAIL_HEADER_PREFIX,FBOOK_URL,INACTIVE_CUTOFF
from django.shortcuts import render_to_response, redirect
from rss import *
from models import *
from views import *
from forms import *

def list(request):
    """Displays groups in a list for browsing.
    
    Displays group name with link to the group's profile.
    Orders and filters the list through form information."""

    login_check(request)

    groups = Group.objects.all()
    
    # Member affiliation data
    affil = {}
    if request.session['user']:
        for group in groups:
            try:
                m = Membership.objects.get(group=group, student=request.session['user'])
                if m.type == 'S':
                    span = '<span style="color:blue;font-weight:bold;">'
                elif m.type == 'M':
                    span = '<span style="color:green;font-weight:bold;">'
                else:
                    span = '<span style="color:orange;font-weight:bold;">'
                affil.setdefault(group.id, span+m.type+'</span>')
            except:
                affil.setdefault(group.id, '')
            try:
                m = MembershipRequest.objects.get(group=group, student=request.session['user'])
                affil[group.id] = '<span style="color:red;font-weight:bold;">R</span> ' + affil[group.id]
            except:
                pass            
    
#    raise Exception(affil)

    # List organization
    if 'switch_cat' in request.GET:
        groups.order_by('category')
        return render_to_response('groups/browse_cat.html', 
                                  {'user':request.session['user'],
                                   'categories':request.session['categories'],
                                   'groups':groups,
                                   'affil':affil,
                                   'alpha':request.session['alpha'],})

    return render_to_response('groups/browse_name.html', 
                       {'user':request.session['user'],
                        'categories':request.session['categories'],
                        'groups':groups,
                        'affil':affil,
                        'alpha':request.session['alpha'],})

def category(request, category):
    """Displays a list of groups in <category>.
    
    Displays group name with link to the group's profile."""

    login_check(request)

    try:
        cat = Category.objects.get(category=category)
    except:
        redirect_index(request)
    groups = Group.objects.filter(categories=cat)

    # Member affiliation data
    affil = {}
    if request.session['user']:
        for group in groups:
            try:
                m = Membership.objects.get(group=group, student=request.session['user'])
                if m.type == 'S':
                    span = '<span style="color:blue;font-weight:bold;">'
                elif m.type == 'M':
                    span = '<span style="color:green;font-weight:bold;">'
                else:
                    span = '<span style="color:orange;font-weight:bold;">'
                affil.setdefault(group.id, span+m.type+'</span>')
            except:
                affil.setdefault(group.id, '')
            try:
                m = MembershipRequest.objects.get(group=group, student=request.session['user'])
                affil[group.id] = '<span style="color:red;font-weight:bold;">R</span> ' + affil[group.id]
            except:
                pass


    return render_to_response('groups/category.html', 
                              {'user':request.session['user'],
                               'category':cat,
                               'categories':request.session['categories'],
                               'groups':groups,
                               'affil':affil,
                               'alpha':request.session['alpha'],})


def profile(request, group):
    """Displays the group profile page."""

    logged_in = login_check(request)

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # If user, check for user-specific data
    if logged_in:
        try:
            user_mship = Membership.objects.get(group=g, student=request.session['user'])
        except:
            user_mship = None
        try:
            user_req = MembershipRequest.objects.get(group=g,student=request.session['user'])
        except:
            user_req = None                         
    else:
        user_mship = None
        user_req = None                         

    # Exclude member who set displays to exclude user
    if not user_mship:
        exclude = ['G','S']
    elif user_mship.type == 'S':
        exclude = ['G']
    else:
        exclude = []

    # Memberships and officers for display purposes
    mships = Membership.objects.filter(group=g, type='M').exclude(display__in=exclude).order_by('?')[:10]
    officers = Membership.objects.filter(group=g, type='O').order_by('-has_order','officer_order')

    # Primary officer info
    try:
        primary = Membership.objects.filter(group=g,officer_order=1)[0]
    except:
        primary = None

    # RSS feed link
    rss_url = SITE_URL+"feeds/groups/%s/"%g.url
    entries = Entry.objects.filter(group=g)[:5]

    # For Sidebar display
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

    # group links
    links = Link.objects.filter(group=g)

    # group files
    if not request.session['user']:
        view_list=['P']
    elif not user_mship:
        view_list=['P','L']
    elif user_mship.type == 'S':
        view_list=['P','L','S']
    elif user_mship.type == 'M':
        view_list=['P','L','S','M']
    else:
        view_list=['P','L','S','M','O']
    files = GroupFile.objects.filter(group=g, permissions__in=view_list)

    # check if group is active
#    if (datetime.now() - g.last_update) > INACTIVE_CUTOFF:
#        inactive=True
#    else:
#        inactive=False

    return render_to_response('groups/profile.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'mships':mships,
                               'officers':officers,
                               'group':g,
                               'entries':entries,
#                               'inactive':inactive,
                               'links':links,
                               'files':files,
                               'primary':primary,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'user_req':user_req,
                               'requests':requests.count(),
                               'rss_url':rss_url,
                               'user_req':user_req,
                               'alpha':request.session['alpha'],
                               'profilepage':True})

def request(request, group):
    """Submits a membership request."""

    logged_in = login_check(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # check if membership already exits
    try:
        Membership.objects.get(group=g,student=request.session['user'],type__in=['M','O'])
        return redirect_index(request)
    except:
        pass

    # check if request already exists
    try:
        MembershipRequest.objects.get(group=g,student=request.session['user'])
        return redirect_index('/groups/%s/'%group)
    except:
        pass

    # Process form
    confirm_msg = ''
    err_msg = ''
    uncheck=[]
    if request.method == 'POST':
        # Create a request from the form
        m=MembershipRequest(student=request.session['user'],group=g)
        form = MshipRequestForm(request.POST, instance=m)
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
            if s.request_notifications=='N' and form.cleaned_data['request_notifications']==True:
                s.request_notifications = 'G'
            if s.request_notifications=='Y' and form.cleaned_data['request_notifications']==False:
                s.request_notifications = 'G'
            if s.message_notifications=='N' and form.cleaned_data['message_notifications']==True:
                s.message_notifications = 'G'
            if s.message_notifications=='Y' and form.cleaned_data['message_notifications']==False:
                s.message_notifications = 'G'
            s.save()
            request.session['user'] = s

            # Email notifications to officers of group
            officers = Membership.objects.filter(group=g,type='O',request_notifications=True)
            list = []
            for o in officers:
                list.append(o.student.email)
            send_mail(EMAIL_HEADER_PREFIX+'Membership Request to \"%s\"'%(g.name,), MSHIP_REQUEST_EMAIL % (g.name,s.full_name,g.url), SITE_EMAIL, list, fail_silently=False)

            return redirect('/groups/%s'%g.url)

        else:
            err_msg = 'There were errors with the following fields:'
    else:
        # New form
        form = MshipRequestForm()
        
        # Reconcile global/local notification settings
        if request.session['user'].mship_notifications=='N':
            uncheck.append('#id_mship_notifications')
        if request.session['user'].feed_notifications=='N':
            uncheck.append('#id_feed_notifications')
        if request.session['user'].message_notifications=='N':
            uncheck.append('#id_message_notifications')
        if request.session['user'].request_notifications=='N':
            uncheck.append('#id_request_notifications')

    # Data for sidebar displays
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
            user_mship = None

    return render_to_response('groups/subscribe.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'uncheck':uncheck,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'request':True,
                               'form':form})

def subscribe(request, group):
    """Subscribe user to group.
    
    Creates a membership object with subscriber permissions."""

    logged_in = login_check(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # Check for existing membership
    try:
        Membership.objects.get(group=g,student=request.session['user'])
        return redirect_index(request)
    except:
        pass

    # process form
    confirm_msg = ''
    err_msg = ''
    uncheck = []
    if request.method == 'POST':
        # Create membership
        m=Membership(student=request.session['user'],group=g, type='S',display='A')
        form = MshipSettingsForm(request.POST, instance=m)
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
            s.save()
            
            request.session['user'] = s
            return redirect('/groups/%s'%g.url)
        else:
            err_msg = 'There were errors with the following fields:'
    else:
        # New form
        form = MshipSettingsForm()

        # Reconcile global/local notification settings
        if request.session['user'].mship_notifications=='N':
            uncheck.append('#id_mship_notifications')
        if request.session['user'].feed_notifications=='N':
            uncheck.append('#id_feed_notifications')
        if request.session['user'].message_notifications=='N':
            uncheck.append('#id_message_notifications')
        if request.session['user'].request_notifications=='N':
            uncheck.append('#id_request_notifications')

    # Info for displying in sidebars
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/subscribe.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'uncheck':uncheck,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'form':form})

def search(request):
    """Searching groups.

    Searches by title and category."""

    login_check(request)

    # Process form
    if request.method == 'GET':
        form = SearchForm(request.GET)
    else:
        form = SearchForm()
    
    # filter by form data
    if form.is_valid():
        if 'search' in form.cleaned_data and form.cleaned_data['search']:
            if 'category' in form.cleaned_data and form.cleaned_data['category']:
                groups = Group.objects.filter(name__icontains=form.cleaned_data['search'],categories=form.cleaned_data['category'])
            else:
                groups = Group.objects.filter(name__icontains=form.cleaned_data['search'])
        else:
            if 'category' in form.cleaned_data and form.cleaned_data['category']:
                groups = Group.objects.filter(categories=form.cleaned_data['category'])
            else:
                groups = Group.objects.all()

    # Paginate
    p = Paginator(groups, SEARCH_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        groups = page.object_list
    except:
        page = p.page(p.num_pages)
        groups = page.object_list

    # Member affiliation data
    affil = {}
    if request.session['user']:
        for group in groups:
            try:
                m = Membership.objects.get(group=group, student=request.session['user'])
                if m.type == 'S':
                    span = '<span style="color:blue;font-weight:bold;">'
                elif m.type == 'M':
                    span = '<span style="color:green;font-weight:bold;">'
                else:
                    span = '<span style="color:orange;font-weight:bold;">'
                affil.setdefault(group.id, span+m.type+'</span>')
            except:
                affil.setdefault(group.id, '')
            try:
                m = MembershipRequest.objects.get(group=group, student=request.session['user'])
                affil[group.id] = '<span style="color:red;font-weight:bold;">R</span> ' + affil[group.id]
            except:
                pass

    return render_to_response('groups/search.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'form':form,
                               'p':p,
                               'affil':affil,
                               'page':page,
                               'groups':groups})

def member_list(request, group):
    """Lists members of a group in a searchable table."""

    if not login_check(request):
        return redirect_index(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
    except:
        user_mship = None
     
    if not user_mship or user_mship.type == 'S':
        if not g.show_members:
            return redirect('/groups/%s/'%group)

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
        # No search data
        form = SearchMemberForm()
        f_name_query = ''
        l_name_query = ''
        netid_query = ''
        year_query = None
        rank_query = ['M','O']

    # Sort
    order_by = 'rank'
    sort = 'name'
    if 'sort' in request.GET:
        if request.GET['sort'] == 'netid':
            order_by='student__netid'
        elif request.GET['sort'] == 'name':
            order_by='student__last_name'
        elif request.GET['sort'] == 'year':
            order_by='student__year'
        elif request.GET['sort'] == 'rank':
            order_by='rank'
        sort = request.GET['sort']
    else:
        order_by='student__last_name'

    # filter according to display preferences
    try:
        m = Membership.objects.get(group=g, student=request.session['user'])
        if m.type == 'S':
            filter_list = ['A','S']
        else:
            filter_list = ['A','S','G']
    except:
        filter_list = ['A']
        m=None
    if not user_mship:
        exclude = ['G','S']
    elif user_mship.type == 'S':
        exclude = ['G']
    else:
        exclude = []

    # Get members
    if year_query:
        if order_by == 'rank':
            mships = Membership.objects.filter(group=g, display__in=filter_list, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query,student__year__exact=year_query).exclude(display__in=exclude).order_by('-type','-has_order','officer_order')
        else:
            mships = Membership.objects.filter(group=g, display__in=filter_list, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query,student__year__exact=year_query).exclude(display__in=exclude).order_by(order_by)
    else:
        if order_by == 'rank':
            mships = Membership.objects.filter(group=g, display__in=filter_list, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query).exclude(display__in=exclude).order_by('-type','-has_order','officer_order')
        else:
            mships = Membership.objects.filter(group=g, display__in=filter_list, type__in=rank_query,student__first_name__icontains=f_name_query,student__last_name__icontains=l_name_query,student__netid__icontains=netid_query).exclude(display__in=exclude).order_by(order_by)

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

    # sidebar data for display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_req = MembershipRequest.objects.get(group=g, student=request.session['user'])
    except:
        user_req = None

    return render_to_response('groups/members.html',
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'p':p,
                               'sort': sort,
                               'form':form,
                               'page':page,
                               'fbook':FBOOK_URL,
                               'group':g,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'requests':requests.count(),
                               'mships':mships,
                               'user_req':user_req,
                               'user_mship':m})

def withdraw(request, group):
    if not login_check(request):
        return redirect_index(request)
    try:
        g = Group.objects.get(url=group)
    except:
        return redirect_index(request)

    try:
        req = MembershipRequest.objects.get(group=g,student=request.session['user'])
    except:
        return redirect('/groups/%s/'%g.url)

    req.delete()

    return redirect('/groups/%s/'%g.url)
