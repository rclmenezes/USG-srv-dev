# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from dsml import gdi
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import *
from views import *
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django import forms
import json
import sys
import time

def check_undergraduate(username):
    # Check if user can be here
    try:
        user = User.objects.get(netid=username)
    except:
        info = gdi(username)
        user = User(netid=username, firstname=info.get('givenName'), lastname=info.get('sn'), pustatus=info.get('pustatus'))
        if info.get('puclassyear'):
            user.puclassyear = int(info.get('puclassyear'))
        user.save()
        #Create queues for each draw
        for draw in Draw.objects.all():
            queue = Queue(draw=draw)
            queue.save()
            user.queues.add(queue)
    if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
        return user
    return None

@login_required
def index(request):
    draw_list = Draw.objects.order_by('id')
    mapscript = mapdata()
    drawscript = drawdata()
#    return HttpResponse(request.user.username);
    user = check_undergraduate(request.user.username)

    if not user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        handle_settings_form(request, user)

    return render_to_response('rooms/base_dataPanel.html', locals())

@login_required
def draw(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    room_list = Room.objects.filter(building__draw__id=drawid)
    return render_to_response('rooms/drawtab.html', locals())

def mapdata():
    buildings = Building.objects.order_by('id')
    maplist = []
    for building in buildings:
        draws = []
        for draw in building.draw.all():
            draws.append(draw.id)
        maplist.append({'name':building.name, 'draws':draws,
                        'lat':building.lat, 'lon':building.lon})
    mapstring = json.dumps(maplist)
    mapscript = '<script type="text/javascript">mapdata = %s</script>' % mapstring
    return mapscript

def drawdata():
    draws = Draw.objects.order_by('id')
    drawlist = []
    for draw in draws:
        drawlist.append({'name':draw.name, 'id':draw.id})
    drawstring = json.dumps(drawlist)
    drawscript = '<script type="text/javascript">drawdata = %s</script>' % drawstring
    return drawscript

# Single room view function
@login_required
def get_room(request, roomid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    room = get_object_or_404(Room, pk=roomid)
    return HttpResponse('Win!')
    
@login_required
def create_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    draw = Draw.objects.get(pk=drawid)
    # Check if user already has queue for this draw
    if user.queues.filter(draw=draw):
        return HttpResponse("fail")
    queue = Queue(draw=draw)
    queue.save()
    user.queues.add(queue)
    return HttpResponse("pass")
    
@login_required
def update_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    draw = Draw.objects.get(pk=drawid)
    qlist = json.loads(request.POST['queue'])
    # resp = ''
    # for r in qlist:
    #     resp += ' ' + r;
    queue = user.queues.filter(draw=draw)[0]
    if not queue:
        return HttpResponse('no queue')
    rooms = []
    for roomid in qlist:
        room = Room.objects.get(pk=roomid)
        if (not room) or not draw in room.building.draw.all():
            return HttpResponse('bad room/draw')
        rooms.append(room)
    # Clear out the old list
    queue.queuetoroom_set.all().delete()
    # Put in new relationships
    for i in range(0, len(rooms)):
        qtr = QueueToRoom(queue=queue, room=rooms[i], ranking=i)
        qtr.save()
    # Test output - list rooms
    return HttpResponse(rooms)

# Ajax for displaying this user's queue
@login_required
def get_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    try:
        queue = user.queues.get(draw__id=drawid)
    except:
        return HttpResponse('no queue')
    queueToRooms = QueueToRoom.objects.filter(queue=queue).order_by('ranking')
    if not queueToRooms:
        return HttpResponse('')
    room_list = []
    for qtr in queueToRooms:
        room_list.append(qtr.room)
    return render_to_response('rooms/queue.html', {'room_list':room_list})

# Send a queue invite
@login_required
def invite_queue(request):
    try:
        draw_id = int(request.POST['draw_id'])
        netid = request.POST['netid']
    except:
        return HttpResponse('')
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    try:
        receiver = User.objects.get(netid=netid)
        draw = Draw.objects.get(pk=draw_id)
    except:
        return HttpResponse('Bad netid/draw id')
    invite = QueueInvite(sender=user, receiver=receiver, draw=draw,
                         timestamp=int(time.time()))
    invite.save()
    return HttpResponse('Ok')

# Respond to a queue invite
@login_required
def respond_queue(request):
    try:
        invite_id = int(request.POST['invite_id'])
        accepted = int(request.POST['accepted'])
    except:
        return HttpResponseForbidden()
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    try:
        invite = user.q_recieved_set.get(pk=invite_id)
    except:
        return HttpResponse('no invite')
    try:
        if accepted:
            invite.accept()
        else:
            invite.deny()
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse('good')

@login_required
#for testing
def review(request, roomid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    try:
        room = Room.objects.get(id=roomid)
    except Room.DoesNotExist:
        return HttpResponseRedirect(reverse(index))
        
    pastReview = None
    try:
        pastReview = Review.objects.get(room=room, user=user)    #the review that the user has posted already (if it exists)
    except Review.DoesNotExist:
        pass
        
    if request.method == 'POST':
        review = request.POST.get('review', None)
        submit = request.POST.get('submit', None)
        display = request.POST.get('display', None)
        delete = request.POST.get('delete', None)
        
        # user asked to review the current room
        if review:
            if pastReview:
                form = ReviewForm(instance=pastReview)
                return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': False, 'edit': True})
            else:   
                form = ReviewForm()
                return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': False})
                
        #user asked to display current reviews
        elif display:
            revs = Review.objects.filter(room=room)
            print 'num reviews found: %d' % (len(revs))
            return render_to_response('rooms/reviewtest.html', {'reviews': revs, 'display': display})
        # user submitted the review
        elif submit:
            if pastReview:
                form = ReviewForm(request.POST, instance=pastReview)
            else:
                form = ReviewForm(request.POST)
                
            if form.is_valid():
                print 'ok valid'
                rev = form.save(commit=False)
                rev.user = user
                rev.room = room
                rev.save()
                return render_to_response('rooms/reviewtest.html', {'submitted': True})
            else:
                form = ReviewForm()
                return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': True, 'error': 'Invalid submit data'})
        elif delete:
            if pastReview:
                pastReview.delete()
                return render_to_response('rooms/reviewtest.html', {'deleted': True})
        else:
            #someone's messing with the post params
            return HttpResponseRedirect(reverse(index))
    else:
        return render_to_response('rooms/reviewtest.html', {'submitted': False})

def settings(q):
    return render_to_response('rooms/usersettings.html')

def handle_settings_form(request, user):
    
    phone = int(request.POST['phone'])
    code = phone * 3 + user.id
    content = "Your confirmation code is: %s" % code
    carriers = Carrier.objects.order_by('name')
    
    for carrier in carriers:
        print carrier.address
        send_mail("", content, 'rooms@tigerapps.org',
              ["%s@%s" % (phone, carrier.address)], fail_silently=False)
