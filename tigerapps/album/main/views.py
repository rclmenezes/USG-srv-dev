"""Django views for the pages on TigerAlbum."""

import os
from cStringIO import StringIO
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail

from album.main.models import Photo, Comment
from album.gpsinfo import parse_gps_info, GPSInfoError

class JPEGField(forms.ImageField):
    """An image field for JPEG images"""

    def to_python(self, data):
        """Checks that the uploaded data contains a valid image *and*
        is a JPEG only."""

        # The following code is copied from Django.
        f = super(JPEGField, self).to_python(data)
        if f is None:
            return None

        if hasattr(data, 'temporary_file_path'):
            filelike = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                filelike = StringIO(data.read())
            else:
                filelike = StringIO(data['content'])

        # OUR CODE! Get excited.
        image = Image.open(filelike)
        image.load()
        if not image.format.lower() == 'jpeg':
            raise ValidationError('Image must be a JPEG.')

        # Again, copied from Django.
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

class SubmitForm(forms.Form):
    photo = JPEGField()
    caption = forms.CharField(required=False, max_length=500)

class SubmitLocateForm(forms.Form):
    xpos = forms.FloatField()
    ypos = forms.FloatField()
    
def delete_comment(comment):
    """Deletes the specified comment."""

    if (len(comment.children.all()) == 0):
        parent = comment.parent
        comment.delete()
        if (parent != None):
            if ((parent.comment == '*This comment has been deleted.*') and
                (parent.author == '')):
                delete_comment(parent)
    else:
        comment.n_flagged = 0
        comment.author = ''
        comment.comment = '*This comment has been deleted.*'
        comment.save()
        
def send_feedback(email, msg):
    """Sends a feedback message from the specified e-mail to the TigerAlbum
    team."""
    send_mail('TigerAlbum Feedback from <%s>' % email,
              msg,
              'TigerAlbum Team <team@tigeralbum.com>',
              ['team@tigeralbum.com'],
              fail_silently=False)

##############
# The views. #
##############

def locate(photo):
    """Attempts to get GPS info from an image."""
    info = Image.open(photo)._getexif()
    if not info:
        return None, None

    for tag, value in info.iteritems():
        if not TAGS.get(tag, tag) == 'GPSInfo':
            continue
        try:
            return parse_gps_info(value)
        except GPSInfoError:
            return None, None
    return None, None

def submit(request):
    """Displays the UI for photo submissions as well as handling the
    resulting HTTP POST request. Uses django.forms for validation."""
    
    context = RequestContext(request)
    if request.method == 'GET':
        return render_to_response(
            'submit.html', { 'form': SubmitForm() }, context)

    form = SubmitForm(request.POST, request.FILES)
    if not form.is_valid():
        # Invalid form. Return to sender for fixing up.
        return render_to_response(
            'submit.html', { 'form': form }, context)

    # Form validated! Time to put data into database.
    photograph = form.cleaned_data['photo']
    caption = form.cleaned_data['caption']
    xpos, ypos = locate(photograph)
    ip = request.META['REMOTE_ADDR']

    photo = Photo(caption=caption,
                  location_x=xpos,
                  location_y=ypos,
                  approved=False,
                  dt_submitted=datetime.today(),
                  n_flagged=0,
                  n_flagged_offs=0,
                  n_flagged_cprv=0,
                  n_flagged_othr=0,
                  n_likes=0,
                  ip=ip)
    photo.save_with(photograph)
    return redirect('album.main.views.submit_update', id=photo.id)

def submit_update(request, id):
    """Asks the user to click on the map and select a location for his
    photograph."""

    try:
        photo = Photo.objects.get(pk=int(id))
    except Photo.DoesNotExist:
        return render_to_response('errors.html',
                                  { 'errors': ["Could not find photograph"] })

    context = RequestContext(request)
    if request.method == 'GET':
        return render_to_response('submit_update.html',
                                  { 'photo': photo }, context)

    form = SubmitLocateForm(request.POST, request.FILES)
    if not form.is_valid():
        # This should never happen, hence the user unfriendliness.
        return HttpResponseServerError('Invalid coordinates %s' % form.errors)

    photo.location_x = form.cleaned_data['xpos']
    photo.location_y = form.cleaned_data['ypos']
    photo.save()
    request.session['alert'] = True
    return redirect('/')

def search(request):
    """Returns search results for the given query."""

    if not 'q' in request.GET:
        return render_to_response('errors.html',
                                  { 'errors': ["Invalid query"] })

    query = request.GET['q']
    if len(query) < 3:
        return render_to_response('errors.html',
{ 'errors': ["Queries must be three characters or more"] })

    photos = Photo.search(query)
    photos = sorted(photos, reverse=True, key=lambda p: p.dt_submitted)
    return render_to_response('search.html',
                              { 'query': query, 'photos': photos })

def common_ip():
    submitted_photos = Photo.objects.filter(approved=False).exclude(location_x=None).exclude(location_y=None).order_by('ip')

    if len(submitted_photos) == 0:
        return (0, 0)

    current_ip = submitted_photos[0].ip
    most_common_ip = current_ip
    count = 0
    most_common_count = count

    for photo in submitted_photos:
        if photo.ip == current_ip:
            count = count + 1
        else:
            if count > most_common_count:
                most_common_ip = current_ip
                most_common_count = count
            current_ip = photo.ip
            count = 1

    if count > most_common_count:
        return (current_ip, count)
    else:
        return (most_common_ip, most_common_count)

def main(request):
    """The main view."""

    data = {
        'alert': False,
        'feedback': False,
        }

    if request.session.get('alert'):
        data['alert'] = True
        request.session['alert'] = False
    if request.session.get('feedback'):
        data['feedback'] = True
        request.session['feedback'] = False
    return render_to_response('main_index.html', data)

#@login_required
def mod_index(request):
    """Index view for moderator actions."""

    if not request.user.is_authenticated():
        return redirect('/login')
    else:
        num_approve_photos = len(Photo.objects.filter(approved=False).exclude(location_x=None).exclude(location_y=None))
        most_common_ip, most_common_count = common_ip()
        last_approval = Photo.objects.filter(approved=True).order_by('-dt_submitted')
        if len(last_approval) > 0:
            date_last_approval = last_approval[0].dt_submitted
        else:
            date_last_approval = 0
        oldest_submit = Photo.objects.filter(approved=False).exclude(location_x=None).exclude(location_y=None).order_by('dt_submitted')
        if len(oldest_submit) > 0:
            date_oldest_submit = oldest_submit[0].dt_submitted
        else:
            date_oldest_submit = 0
        num_flagged_photos = len(Photo.objects.filter(n_flagged__gt=0))
        num_flagged_comments = len(Comment.objects.filter(n_flagged__gt=0))
        return render_to_response('mod_index.html',
                                  {'num_approve_photos':num_approve_photos,
                                   'most_common_ip':most_common_ip,
                                   'most_common_count':most_common_count,
                                   'date_last_approval':date_last_approval,
                                   'date_oldest_submit':date_oldest_submit,
                                   'num_flagged_photos':num_flagged_photos,
                                   'num_flagged_comments':num_flagged_comments},
                                  context_instance=RequestContext(request))


#@login_required
def mod_photo_approve(request):
    """The moderator interface for photo approval."""
    if not request.user.is_authenticated():
        return redirect ('/login')

    if request.method == 'POST':
        try:
            for index in range(1, 11):
                photo_id = request.POST.get(str(index)+'_id')
                photo = Photo.objects.get(id=int(photo_id))
                caption_edit = request.POST.has_key(str(index)+'_ce')
                action = request.POST.get('group_' + str(index))
                if (caption_edit):
                    photo.caption = request.POST.get(str(index)+'_ct')
                    photo.save()
                if (action == 'accept'):
                    photo.approved = True
                    photo.save()
                elif (action == 'reject'):
                    if (os.path.exists(photo.photo.path)):
                        os.remove(photo.photo.path)
                    if (os.path.exists(photo.thumbnail.path)):
                        os.remove(photo.thumbnail.path)
                    comments = photo.comments.all()
                    for comment in comments:
                        comment.delete()
                    photo.delete()
                elif (action == 'pass'):
                    pass
        except:
            pass

    unapproved_list = Photo.objects.filter(approved=False).exclude(location_x=None).exclude(location_y=None).order_by('dt_submitted', 'ip')[:10]
    return render_to_response('photo_approve.html',
                              {'unapproved_list': unapproved_list},
                              context_instance=RequestContext(request))

#@login_required
def mod_photo_approve_ip(request):
    """The moderator interface for photo approval of most common ip."""
    if not request.user.is_authenticated():
        return redirect ('/login')

    if request.method == 'POST':
        try:
            for index in range(1, 11):
                photo_id = request.POST.get(str(index)+'_id')
                photo = Photo.objects.get(id=int(photo_id))
                caption_edit = request.POST.has_key(str(index)+'_ce')
                action = request.POST.get('group_' + str(index))
                if (caption_edit):
                    photo.caption = request.POST.get(str(index)+'_ct')
                    photo.save()
                if (action == 'accept'):
                    photo.approved = True
                    photo.save()
                elif (action == 'reject'):
                    if (os.path.exists(photo.photo.path)):
                        os.remove(photo.photo.path)
                    if (os.path.exists(photo.thumbnail.path)):
                        os.remove(photo.thumbnail.path)
                    comments = photo.comments.all()
                    for comment in comments:
                        comment.delete()
                    photo.delete()
                elif (action == 'pass'):
                    pass
        except:
            pass

    most_common_ip, throwaway = common_ip()
    unapproved_list = Photo.objects.filter(approved=False, ip=str(most_common_ip)).exclude(location_x=None).exclude(location_y=None).order_by('dt_submitted')[:10]
    return render_to_response('photo_approve_ip.html',
                              {'unapproved_list': unapproved_list},
                              context_instance=RequestContext(request))

#@login_required
def mod_photo_review(request):
    """The moderator interface for photo approval."""
    if not request.user.is_authenticated():
        return redirect ('/login')

    if request.method == 'POST':
        try:
            for index in range(1, 11):
                photo_id = request.POST.get(str(index)+'_id')
                photo = Photo.objects.get(id=int(photo_id))
                caption_edit = request.POST.has_key(str(index)+'_ce')
                action = request.POST.get('group_' + str(index))
                if (caption_edit):
                    photo.caption = request.POST.get(str(index)+'_ct')
                    photo.save()
                if (action == 'accept'):
                    photo.n_flagged = 0
                    photo.save()
                elif (action == 'reject'):
                    if (os.path.exists(photo.photo.path)):
                        os.remove(photo.photo.path)
                    if (os.path.exists(photo.thumbnail.path)):
                        os.remove(photo.thumbnail.path)
                    comments = photo.comments.all()
                    for comment in comments:
                        comment.delete()
                    photo.delete()
                elif (action == 'pass'):
                    pass
        except:
            pass

    flagged_list = Photo.objects.filter(n_flagged__gt=0).order_by('-n_flagged')[:10]
    return render_to_response('photo_review.html',
                              {'flagged_list': flagged_list},
                              context_instance=RequestContext(request))

#@login_required
def mod_comment_review(request):
    """The moderator interface for comment approval."""
    if not request.user.is_authenticated():
        return redirect('/login')
    if request.method == 'POST':
        try:
            for index in range(1, 11):
                comment_id = request.POST.get(str(index)+'_id')
                comment = Comment.objects.get(id=int(comment_id))
                author_edit = request.POST.has_key(str(index)+'_ae')
                comment_edit = request.POST.has_key(str(index)+'_ce')
                action = request.POST.get('group_' + str(index))
                if (author_edit):
                    comment.author = request.POST.get(str(index)+'_at')
                    comment.save()
                if (comment_edit):
                    comment.comment = request.POST.get(str(index)+'_ct')
                    comment.save()
                if (action == 'accept'):
                    comment.n_flagged = 0
                    comment.save()
                elif (action == 'reject'):
                    delete_comment(comment)
                elif (action == 'pass'):
                    pass
        except:
            pass


    flagged_comments = Comment.objects.filter(n_flagged__gt=0).order_by('-n_flagged')[:10]
    return render_to_response('comment_review.html',
                              {'flagged_comments':flagged_comments},
                              context_instance=RequestContext(request))

@csrf_protect
def mod_login(request):
    """The login interface for moderators."""
    if request.user.is_authenticated():
        redirect('/mod')

    state = 'Please enter your username and password.'
    username = ''
    password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/mod')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('login.html',
                              {'state': state, 'username': username},
                              context_instance=RequestContext(request))

def mod_logout(request):
    """Logs a moderator out and redirects to the login page."""
    logout(request)
    return redirect('/mod')

def mod_list(request):
    """The moderator interface for photo approval of most common ip."""
    if not request.user.is_authenticated():
        return redirect ('/login')
    mods = User.objects.all()
    return render_to_response('mod_list.html', {'mods':mods})

@csrf_protect
def change_password(request):
    """The moderator interface to change passwords."""
    if not request.user.is_authenticated():
        return redirect('/login')
    if request.method == 'GET':
        return render_to_response('change_password.html',
{'state': 'Please enter your old and new passwords',
 'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        username = request.user.username
        oldpassword = request.POST.get('oldpassword')
        newpassword = request.POST.get('newpassword')
        user = authenticate(username=username, password=oldpassword)
        if user is not None:
            if user.is_active:
                if len(newpassword) < 8:
                    return render_to_response('change_password.html',
{'state': 'New password should be atleast 8 characters long.',
 'username': username},
context_instance=RequestContext(request))
                us = User.objects.get(username__exact=username)
                us.set_password(newpassword)
                us.save()
                return redirect('/mod')
            else:
                return render_to_response('login.html',
{'state': 'Your account is not active, please contact the site admin.',
 'username': username},
context_instance=RequestContext(request))
        else:
            return render_to_response('change_password.html',
{'state': 'Your username and/or current password were incorrect.',
 'username': username},
context_instance=RequestContext(request))

class ContactForm(forms.Form):
    """Form for feedback requests."""
    CHOICES = [
        ('0', 'General feedback about the website'),
        ('1', 'Reporting a bug'),
        ('2', 'Bitching about moderation'),
        ('3', 'Other'),
        ]

    email = forms.EmailField(required=False, max_length=100)
    comment = forms.CharField(widget=forms.widgets.Textarea(),
                              max_length=50000)
    reason = forms.ChoiceField(widget=forms.widgets.RadioSelect(),
                               choices=CHOICES)

CONTACT_TEMPLATE = """
NEW FEEDBACK

From: %s

Reason: %s

Comment:
%s
"""

def contact(request):
    """On GET, returns a nice contact-us form. On POST, parses the
    data and sends an email to team@tigeralbum.com."""

    context = RequestContext(request)
    if request.method == 'GET':
        return render_to_response(
            'contact_us.html', { 'form': ContactForm() }, context)

    form = ContactForm(request.POST)
    if not form.is_valid():
        return render_to_response(
            'contact_us.html', { 'form': form }, context)

    email = form.cleaned_data['email'] or 'anonymous'
    comment = form.cleaned_data['comment']
    reason = form.cleaned_data['reason']
    send_feedback(email, CONTACT_TEMPLATE %
                  (email, ContactForm.CHOICES[int(reason)][1], comment))
    request.session['feedback'] = True
    return redirect('/')
