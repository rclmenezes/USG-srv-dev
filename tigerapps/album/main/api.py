"""API functions for handling JSON interface calls that are used by the
Django server."""

import django.http
import json
from datetime import datetime, timedelta

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import (render_to_response,
                              get_object_or_404)
from django.views.decorators.csrf import csrf_exempt

from tigeralbum.main.models import Photo, Comment

# Number of photos photos() (a.k.a. 'api/photos.json') can return
# at any one time.
PHOTOS_LIMIT = 40

# Priority for displaying popular photos over newer photos
POPULAR_PRIORITY = 1

class JSONError(Exception):
    """An exception class that takes an error message but has a helper
    method to turn the exception into an HttpResponse object that
    contains a JSON representation of the error."""

    def __init__(self, error):
        self.error = error
        super(JSONError, self).__init__(error)

    def response(self):
        """Returns an HttpResponse object with the JSON error."""
        return django.http.HttpResponseServerError('{"error": "%s"}' %
                                                   self.error)

def photos(request):
    """Returns the most popular photos within a given geometrical
    bounds as JSON. Returns an error as JSON if something goes
    awry."""

    GET = request.GET

    def pleasegivemeafloat(key):
        """Returns the float value in the GET query dictionary that
        corresponds to the key. Raises a JSONError if something goes
        awry."""

        value = GET.get(key)
        if not value:
            raise JSONError('Missing %s parameter' % key)
        try:
            return float(value)
        except ValueError:
            raise JSONError('Expected float for %s parameter' % key)

    def pleasegivemeanint(key):
        """Returns the integer value in the GET query dictionary that
        corresponds to the key. Raises a JSONError if something goes
        awry."""

        value = GET.get(key)
        if not value:
            raise JSONError('Missing %s parameter' % key)
        try:
            return int(value)
        except ValueError:
            raise JSONError('Expected integer for %s parameter' % key)

    def pleasegivemeastring(key):
        """Returns the string value in the GET query dictionary that
        corresponds to the key. Raises a JSONError if something goes
        awry."""

        value = GET.get(key)
        if not value:
            raise JSONError('Missing %s parameter' % key)
        try:
            return str(value)
        except ValueError:
            raise JSONError('Expected float for %s parameter' % key)

    def to_dict(photo):
        """Returns a dictionary of keys and values representing a
        Photo model. This dictionary is suitable to be serialized into
        JSON."""

        return dict(id=photo.permalink,
                    location_x=photo.location_x,
                    location_y=photo.location_y,
                    photo=dict(name=photo.photo.name, height=photo.height,
                               width=photo.width),
                    thumbnail=photo.thumbnail.name,
                    popularity=photo.popularity)

    def filter_overlap(photo_list, zoom):
        """Removes photos from photo_list that overlap other photos preceding
        them"""

        new_list = []
        for photo1 in photo_list:
            overlaps = False
            for photo2 in new_list:
                if (photo1.overlaps(photo2, zoom)):
                    overlaps = True
            if (overlaps == False):
                new_list.append(photo1)
        return new_list

    def merge_lists(list1, list2, num):
        """Merges the 2 lists, and returns the num first elements."""
        i1 = 0
        i2 = 0
        combined = []

        while i1 < len(list1) and i2 < len(list2):
            if i1 < len(list1):
                for j in range(POPULAR_PRIORITY):
                    if (i1 >= len(list1)):
                        break
                    if ((list1[i1] in combined) == False):
                        combined.append(list1[i1])
                    i1 += 1
            if i2 < len(list2):
                if ((list2[i2] in combined) == False):
                    combined.append(list2[i2])
        
        return combined[:num]

    def stringtoage(time):
        """Converts the dropdown value from the age filter to a length of
        time."""
        if (time == 'week'):
            return 7*24
        elif (time == 'month'):
            return 30*24
        elif (time == 'year'):
            return 365*24
        else:
            raise ValueError
    try:
        xmin = pleasegivemeafloat('xmin')
        xmax = pleasegivemeafloat('xmax')
        ymin = pleasegivemeafloat('ymin')
        ymax = pleasegivemeafloat('ymax')
        num = pleasegivemeanint('num')
        zoom = pleasegivemeanint('zoom')
        time = pleasegivemeastring('time')

        if xmin >= xmax:
            raise JSONError('xmin must be less than xmax')
        if ymin >= ymax:
            raise JSONError('ymin must be less than ymax')
        if num > PHOTOS_LIMIT:
            raise JSONError('Cannot request more than %d photos' % PHOTOS_LIMIT)

        if (time == 'recent'):
            popular = Photo.popular(xmin, xmax, ymin, ymax, num)
            newest = Photo.newest(xmin, xmax, ymin, ymax, num)
            pics = merge_lists(popular, newest, num)
        elif (time == 'all'):
            pics = Photo.popular(xmin, xmax, ymin, ymax, num)
        else:
            threshold = stringtoage(time)
            pics = Photo.popular_by_age(xmin, xmax, ymin, ymax, num,
                                          threshold)

        pics = filter_overlap(pics, zoom)
        pics = map(to_dict, pics)
        return HttpResponse(json.dumps(dict(photos=pics), indent=2))

    except JSONError, err:
        return err.response()

def getcomments(photo):
    """Returns the comment thread for a photo, sorted and nested and
    everything!"""

    def comment_sorted(comments):
        """Sorts comments by date posted."""
        return sorted(comments, key=lambda c: c.dt_posted)

    topcomments = Comment.posts(photo.id)
    comments = []
    for topcomment in comment_sorted(topcomments):
        comments.append({"depth":0, "comment":topcomment})
        secondcomments = topcomment.children.all()
        for secondcomment in comment_sorted(secondcomments):
            comments.append({"depth":30, "comment":secondcomment})
            thirdcomments = secondcomment.children.all()
            for thirdcomment in comment_sorted(thirdcomments):
                comments.append({"depth":60, "comment":thirdcomment})
    return comments

def details(request):
    """Returns the details for a photo aka everything when a user
    clicks on it"""

    if request.method != 'GET':
        raise Http404

    request_get = request.GET
    permalink = request_get.get('id')
    if not permalink:
        raise Http404

    photo = Photo.get_by_permalink(permalink)
    if not photo.approved:
        raise Http404

    # find size of the image to display (fit into a maxsize by maxsize box)
    maxsize = 600
    height = 0
    width = 0
    if (photo.width < photo.height):
        height = maxsize
        width = round(photo.width / (photo.height/maxsize))
    else:
        width = maxsize
        height = round(photo.height / (photo.width/maxsize))

    data = {
        "photo": photo.photo,
        "permalink": permalink,
        "width": width ,
        "height": height,
        "caption": photo.caption,
        "dt_submitted": photo.dt_submitted.date(),
	"comments": getcomments(photo)
        }
    return render_to_response('details.html', data)

@csrf_exempt
def submit_comment(request):
    if request.method != 'POST':
        raise Http404
    permalink = request.POST.get('id')
    if not permalink:
        raise Http404
    author = request.POST.get('author')
    if (not author) or (author.strip() == ""):
        author = 'Anonymous'
    if (author.strip().lower() == "moderator"):
        author = "Imposter"
    if (len(author) > 25):
        author = author[0:25]
    comment = request.POST.get('comment')
    if (not comment) or (comment.strip() == ""):
        return HttpResponse("")
    parent = request.POST.get('parent')
    if (not parent) or (parent.strip() == ""):
        parentobj = None
    else:
        parentobj = get_object_or_404(Comment, id=parent)
    if (len(comment) > 250):
        comment = comment[0:250]

    photo = Photo.get_by_permalink(permalink)
    if not photo:
        raise Http404

    ip = request.META['REMOTE_ADDR']
    #check if user is posting too many comments
    timediff = 0.5 # can only post 1 comment in this many minutes
    recent = Comment.objects.filter(ip=ip,
dt_posted__gte=(datetime.today()-timedelta(minutes=timediff)))
    if (len(recent) > 0):
        return HttpResponse("You are posting too frequently. Please wait a while before posting again")
        #return
    new_comment = Comment(photo=photo, parent=parentobj, comment=comment,
                          author=author, dt_posted=datetime.today(),
                          n_flagged=0, ip=ip)
    new_comment.save()
    return HttpResponse("")

def comments(request):
    if request.method != 'GET':
        raise Http404

    permalink = request.GET.get('id')
    if not permalink:
        raise Http404

    photo = Photo.get_by_permalink(permalink)
    if not photo:
        raise Http404

    return render_to_response('api_comments.html',
                              {'comments': getcomments(photo) })

def like(request):
    if request.method != 'GET':
        raise Http404

    permalink = request.GET.get('id')
    if not permalink:
        raise Http404

    photo = Photo.get_by_permalink(permalink)
    if not photo:
        raise Http404

    photo.n_likes += 1
    photo.save()
    return HttpResponse(photo.n_likes)

def report_image(request):
    if request.method != 'GET':
        raise Http404

    permalink = request.GET.get('id')
    if not permalink:
        raise Http404

    reason = request.GET.get('reason')
    if not reason:
        raise Http404

    photo = Photo.get_by_permalink(permalink)
    if not photo:
        raise Http404

    photo.n_flagged += 1
    if reason == 'offs':
        photo.n_flagged_offs = photo.n_flagged_offs + 1
    elif reason == 'cprv':
        photo.n_flagged_cprv = photo.n_flagged_cprv + 1
    elif reason == 'othr':
        photo.n_flagged_othr = photo.n_flagged_othr + 1
    photo.save()

    return HttpResponse(photo.n_flagged)

def report_comment(request):
    if request.method != 'GET':
        raise Http404
    commentid = request.GET.get('id')
    if not commentid:
        raise Http404
    comment = get_object_or_404(Comment, id=commentid)
    comment.n_flagged = comment.n_flagged + 1
    comment.save()
    return HttpResponse(comment.n_flagged)
