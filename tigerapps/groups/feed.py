# feed.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for posting to feeds, sending messages

from django.core.paginator import Paginator
from globalsettings import SITE_URL,SITE_EMAIL,TABLE_ENTRIES_PER_PAGE,BLOG_ENTRIES_PER_PAGE,EMAIL_HEADER_PREFIX
from email_msg import *
from django.core.mail import send_mail
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from models import *
from views import *
from groups import *
from forms import *

def post(request, group):
    """Post to a group newsfeed."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)
    
    # create Entry object
    e = Entry(group=g)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            
            # Email notifications
            mships = Membership.objects.filter(group=g,feed_notifications=True)
            list = []
            for m in mships:
                list.append(str(m.student.email))
            send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Posted to its Feed'%g.name, FEED_NOTIFICATION_EMAIL % (g.name, form.cleaned_data['title'], form.cleaned_data['text'],g.url), SITE_EMAIL, list, fail_silently=False)

            return redirect('/groups/%s/'%group)
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        # new form
        form = EntryForm(instance=e)

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
    
    return render_to_response('groups/post.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'requests':requests.count(),
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})
                             
def edit_post(request, group, entry):
    """Edit a newsfeed post."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # get the entry
    try:
        e = Entry.objects.get(id=entry)
    except:
        return redirect_index(request)

    # get location info
    if 'newsfeed' in request.GET:
        newsfeed = True
        if 'page' in request.GET:
            page = request.GET['page']
    else:
        newsfeed = False
        page = None

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # Save changes
        form = EntryForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            if 'newsfeed' in request.POST:
                if 'page' in request.POST and request.POST['page']:
                    return redirect("/groups/%s/feed?page=%s"%(group,request.GET['page']))
                else:
                    return redirect("/groups/%s/feed/"%(group,))
            else:
                return redirect("/groups/%s/"%group)
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        # new form
        form = EntryForm(instance=e)
    
    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/post.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'entry':e,
                               'newsfeed':newsfeed,
                               'page':page,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'requests':requests.count(),
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})
                             
def delete_post(request, group, entry):
    """Delete a newsfeed entry."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s/"%group)

    # get entry
    try:
        e = Entry.objects.get(id=entry)
    except:
        return redirect_index(request)

    e.delete()
    if 'newsfeed' in request.GET:
        if 'page' in request.GET and request.GET['page']:
            return redirect("/groups/%s/feed?page=%s"%(group,request.GET['page']))
        else:
            return redirect("/groups/%s/feed/"%(group,))
    else:
        return redirect("/groups/%s/"%group)

def send_message(request, group):
    """Send a message to group members."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # create message
        m = Message(group=g,author=request.session['user'])
        form = MessageForm(request.POST, instance=m)
        if form.is_valid():
            form.save()

            # Add group members to 'unread' list
            if form.cleaned_data['view_permissions']=='O':
                view_list = ['O']
            else:
                view_list = ['M','O']
            students = Student.objects.filter(membership__group=g,membership__type__in=view_list)
            m = Message.objects.get(pub_date=form.instance.pub_date)
            for s in students:
                m.unread.add(s)
            m.save()

            # Email notifications
            if form.cleaned_data['view_permissions'] == 'M':
                view_list = ['M','O']
            else:
                view_list = ['O']
            mships = Membership.objects.filter(group=g, type__in=view_list, message_notifications=True)
            list = []
            for mship in mships:
                list.append(str(mship.student.email))
            send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Sent a Message'%g.name, MESSAGE_NOTIFICATION_EMAIL % (g.name, form.cleaned_data['title'], form.cleaned_data['text'],g.url,m.id), SITE_EMAIL, list, fail_silently=False)
            m = Message.objects.get(pub_date=form.instance.pub_date)
            return redirect('/groups/%s/messages/%d/' % (group,m.id))
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        # new form
        form = MessageForm()

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None
    
    return render_to_response('groups/send_message.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'requests':requests.count(),
                               'reactivate_req':reactivate_req,
                               'form':form,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})

def edit_message(request, group, message):
    """Edit a message."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    # get message
    try:
        m = Message.objects.get(id=message)
    except:
        return redirect_index(request)

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # make changes
        form = MessageForm(request.POST, instance=m)
        if form.is_valid():
            form.save()
            return redirect('/groups/%s/messages/%s' % (group,message))
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        # new form
        form = MessageForm(instance=m)
    
    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/send_message.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'message':m,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'form':form,
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})

def group_messages(request, group):
    """Table of all messages for this group."""

    if not login_check(request):
        redirect_index(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # user must be member
    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
    except:
        redirect('/group/%s'%group)
        
    # search
    if request.method == 'GET':
        form = SearchGroupMessageForm(request.GET)
        if form.is_valid():
            if 'search' in form.cleaned_data and form.cleaned_data['search']:
                query = form.cleaned_data['search']
            else:
                query = ''
            if 'date' in form.cleaned_data and form.cleaned_data['date']:
                date_query = datetime(form.cleaned_data['date'].year,form.cleaned_data['date'].month,form.cleaned_data['date'].day)
            else:
                date_query = None
        else:
            query = ''
            date_query = None
            form = SearchGroupMessageForm()
    else:
        query = ''
        date_query = None
        form = SearchGroupMessageForm()
        
    # view permissions
    if user_mship.type == 'M':
        view_list = ['M']
    else:
        view_list = ['M','O']

    # get messages from db
    if date_query:
        messages = Message.objects.filter(group=g, view_permissions__in=view_list, title__icontains=query,pub_date__year=date_query.year,pub_date__month=date_query.month,pub_date__day=date_query.day)
    else:
        messages = Message.objects.filter(group=g, view_permissions__in=view_list, title__icontains=query)

    # Paginate messages
    p = Paginator(messages, TABLE_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        messages = page.object_list
    except:
        page = p.page(p.num_pages)
        messages = page.object_list

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/group_messages.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'p':p,
                               'page':page,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,                     
                               'messages':messages,
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'alpha':request.session['alpha'],})

def delete_group_message(request, group, message):
    """Delete a message."""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)
    if not officer_check(request, g):
        return redirect("/groups/%s"%group)

    try:
        m = Message.objects.get(id=message)
    except:
        return redirect_index(request)

    m.delete()
    return redirect('/groups/%s/messages'%g.url)

def read_group_message(request, group, message):
    """Display a message for reading, commenting."""

    if not login_check(request):
        redirect_index(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # user must be member
    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
    except:
        redirect('/group/%s'%group)

    # user must have proper view permissions
    if user_mship.type == 'M':
        view_list = ['M']
    else:
        view_list = ['M','O']
    try:
        m = Message.objects.get(id=message, view_permissions__in=view_list)
    except:
        return redirect('/groups/%s/messages'%group)

    # User has now read message
    if request.session['user'] in m.unread.all():
        m.unread.remove(request.session['user'])

    # get comments on this message
    comments = MessageComment.objects.filter(message=m)

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/read_group_message.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'message_page':True,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,                        
                               'message':m,
                               'comments':comments,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'alpha':request.session['alpha'],})


def comment_group_message(request, group, message):
    """Form for commenting on a message."""

    if not login_check(request):
        redirect_index(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # user must be group member
    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
    except:
        redirect('/group/%s'%group)

    # user must have view permission
    if user_mship.type == 'M':
        view_list = ['M']
    else:
        view_list = ['M','O']
    try:
        m = Message.objects.get(id=message, view_permissions__in=view_list)
    except:
        return redirect('/groups/%s/messages'%group)

    # make sure comments are allowed
    if m.comment_permissions == 'C':
        return redirect('/groups/%s/messages/%s' % (group,m.id))

    # process form
    err_msg = ''
    confirm_msg = ''
    if request.method == 'POST':
        # submit comment
        c = MessageComment(message=m,comment_author=request.session['user'])
        form = MessageCommentForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            return redirect('/groups/%s/messages/%s' % (group,message))
        else:
            err_msg = 'There were errors in the following fields: '
    else:
        # new form
        form = MessageCommentForm()
    
    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
        user_mship = None

    return render_to_response('groups/comment_group_message.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'message':m,
                               'requests':requests.count(),
                               'form':form,
                               'user_mship':user_mship,
                               'reactivate_req':reactivate_req,
                               'unread_messages':unread.count(),
                               'err_msg':err_msg,
                               'confirm_msg':confirm_msg,
                               'alpha':request.session['alpha'],})

def delete_comment(request, group, message, comment):
    """Delete a comment on a message"""

    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # message and comment must exist and match
    try:
        c = MessageComment.objects.get(id=comment)
        m = Message.objects.get(id=message)
        if m != c.message:
            raise Exception()
        # user must have permission
        if (not officer_check(request,g)) and request.session['user'] != c.comment_author:
            raise Exception()
    except:
        return redirect('/group/%s'%group)

    c.delete()
    
    if 'commentpage' in request.GET:
        if 'page' in request.GET:
            return redirect('/groups/%s/messages/%d/read_comments?page=%s'%(g.url,m.id,request.GET['page']))
        else:
            return redirect('/groups/%s/messages/%d/read_comments'%(g.url,m.id))
    return redirect('/groups/%s/messages/%d'%(g.url,m.id))

def all_entries(request, group):
    """View all newsfeed entries in searchable format."""

    login_check(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # search form
    if request.method == 'GET':
        form = SearchGroupMessageForm(request.GET)
    else:
        form = SearchGroupMessageForm()
        query = ''
        date_query = None

    if form.is_valid():
        if 'search' in form.cleaned_data and form.cleaned_data['search']:
            query = form.cleaned_data['search']
        else:
            query = ''
        if 'date' in form.cleaned_data and form.cleaned_data['date']:
            date_query = datetime(form.cleaned_data['date'].year,form.cleaned_data['date'].month,form.cleaned_data['date'].day)
        else:
            date_query = None
    else:
        query = ''
        date_query = None
        form = SearchGroupMessageForm()
        
    # get entries
    if date_query:
        entries = Entry.objects.filter(group=g, title__icontains=query,pub_date__year=date_query.year,pub_date__month=date_query.month,pub_date__day=date_query.day)        
    else:
        entries = Entry.objects.filter(group=g, title__icontains=query)

    # Paginate
    p = Paginator(entries, BLOG_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        entries = page.object_list
    except:
        page = p.page(p.num_pages)
        entries = page.object_list

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

    return render_to_response('groups/all_entries.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'p':p,
                               'user_req':user_req,
                               'page':page,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,                     
                               'entries':entries,
                               'form':form,
                               'reactivate_req':reactivate_req,
                               'requests':requests.count(),
                               'alpha':request.session['alpha'],})

def read_comments(request, group, message):
    """View all comments on a message."""

    login_check(request)
    try:
        g = Group.objects.get(url__exact=group)
    except:
        return redirect_index(request)

    # user must be member
    try:
        user_mship = Membership.objects.get(group=g,student=request.session['user'])
        if user_mship.type == 'S':
            raise Exception()
    except:
        return redirect('/groups/%s/'%group)

    # user must have view permission
    if user_mship.type == 'M':
        view_list = ['M']
    else:
        view_list = ['M','O']
    try:
        m = Message.objects.get(id=message, view_permissions__in=view_list)
    except:
        return redirect('/groups/%s/messages'%group)

    # get comments
    comments = MessageComment.objects.filter(message=m)

    # Paginate
    p = Paginator(comments, BLOG_ENTRIES_PER_PAGE)
    if request.method == "GET" and 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    try:
        page = p.page(page)
        comments = page.object_list
    except:
        page = p.page(p.num_pages)
        comments = page.object_list

    # data for sidebar display
    reactivate_req = GroupReactivationRequest.objects.filter(group=g)
    requests = MembershipRequest.objects.filter(group=g)
    unread = Message.objects.filter(group=g,unread=request.session['user'])
    try:
        user_mship = Membership.objects.get(group=g, student=request.session['user'])
    except:
            user_mship = None

    return render_to_response('groups/read_comments.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'group':g,
                               'p':p,
                               'page':page,
                               'message':m,
                               'unread_messages':unread.count(),
                               'user_mship':user_mship,                     
                               'comments':comments,
                               'requests':requests.count(),
                               'reactivate_req':reactivate_req,
                               'alpha':request.session['alpha'],})
