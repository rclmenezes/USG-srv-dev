# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from dsml import gdi
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import *
from views import *
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django import forms
import json
import sys,os
import traceback

if 'IS_REAL_TIME_SERVER' in os.environ:
    from real_time_views import *

REAL_TIME_ADDR='http://dev.rooms.tigerapps.org:8031'
NORMAL_ADDR='http://dev.rooms.tigerapps.org:8017'

def externalResponse(data):
    response =  HttpResponse(data)
    response['Access-Control-Allow-Origin'] =  NORMAL_ADDR
    response['Access-Control-Allow-Credentials'] =  "true"
    return response

def check_undergraduate(username):
    # Check if user can be here
    try:
        user = User.objects.get(netid=username)
    except:
        info = gdi(username)
        user = User(netid=username, firstname=info.get('givenName'), lastname=info.get('sn'), pustatus=info.get('pustatus'))
        if info.get('puclassyear'):
            user.puclassyear = int(info.get('puclassyear'))
        if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
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
    #occlong = occlong()
    #    return HttpResponse(request.user.username);
    user = check_undergraduate(request.user.username)

    if not user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if request.POST['form_type'] == 'settings':
            handle_settings_form(request, user)
    
    response = render_to_response('rooms/base_dataPanel.html', locals())
    response['Access-Control-Allow-Origin'] =  '*'
    return response


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
    mapstring = mapstring + ('; REAL_TIME_ADDR = "%s"' % REAL_TIME_ADDR)
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

def occlonghelper(room):
    occlong = 'Single'
    if room.occ == 1:
        occlong = 'Single'
    elif room.occ == 2:
        occlong = 'Double'
    elif room.occ == 3:
        occlong = 'Triple'
    elif room.occ == 4:
        occlong = 'Quad'
    else:
        occlong = 'Suite' + ' (' + str(room.occ) + ')'
    return occlong
    
def floorwordhelper(floor):
	
	if floor == 0:
		floorword = 'Ground'
	elif floor == 1:
		floorword = 'First'
	elif floor == 2:
		floorword = 'Second'
	elif floor == 3:
		floorword = 'Third'
	elif floor == 4:
		floorword = 'Fourth'
	elif floor == 5:
		floorword = 'Fifth'
	else:
		floorword = 'Zebra'
	return floorword;
		

# Single room view function
@login_required
def get_room(request, roomid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    room = get_object_or_404(Room, pk=roomid)
    occlong = occlonghelper(room)
    floorword = floorwordhelper(room.floor)
    
    # Gather reviews for this room
    revs = Review.objects.filter(room=room)
    print 'num reviews found: %d' % (len(revs))
    
    pastReview = None
    try:
        pastReview = Review.objects.get(room=room, user=user)    #the review that the user has posted already (if it exists)
    except Review.DoesNotExist:
        pass
        
    if request.method == 'POST':
        review = request.POST.get('review', None)
        submit = request.POST.get('submit', None)
        delete = request.POST.get('delete', None)
        
        # user wants to review - clicked "Review this Room"
        if review:
            if pastReview:
                form = ReviewForm(instance=pastReview)
                return render_to_response('rooms/room_view.html', {'room' : room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs, 'form': form, 'edit': True}, context_instance=RequestContext(request))
            else:   
                form = ReviewForm()
                return render_to_response('rooms/room_view.html', {'room' : room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs, 'form': form}, context_instance=RequestContext(request))
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
                revs = Review.objects.filter(room=room)
                print 'num reviews found: %d' % (len(revs))
                return render_to_response('rooms/room_view.html', {'room':room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs})
            else:
                form = ReviewForm()
                return render_to_response('rooms/room_view.html', {'room':room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs, 'form': form, 'error': 'Invalid submit data'})
        # user clicked "Delete this Review"
        elif delete:
            if pastReview:
                pastReview.delete()
                revs = Review.objects.filter(room=room)
                print 'num reviews found: %d' % (len(revs))
                return render_to_response('rooms/room_view.html', {'room':room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs})
    
    return render_to_response('rooms/room_view.html', {'room':room, 'occlong':occlong, 'floorword':floorword, 'reviews':revs})
    
@login_required
def create_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    draw = Draw.objects.get(pk=drawid)
    # Check if user already has queue for this draw
    if user.queues.filter(draw=draw):
        return HttpResponse("fail")
    queue = Queue.make(draw=draw, user=user)
    queue.save()
    user.queues.add(queue)
    return HttpResponse("pass")

# Send a queue invite
@login_required
def invite_queue(request):
    try:
        draws = Draw.objects.all()
        netid = request.POST['netid']
        invited_draws = []
        for draw in draws:
            if int(request.POST['draw%d' % draw.id]):
                invited_draws.append(draw)
    except:
        return HttpResponse('Oops! Your form data is invalid. Try again!')
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()

    try:
        #receiver = User.objects.get(netid=netid)
        receiver = check_undergraduate(netid)
    except:
        return manage_queues(request, 'Sorry, the netid "%s" is invalid. Try again!' % netid)

    if len(invited_draws) == 0:
        return manage_queues(request, 'You didn\'t select any draws. Try again!')

    for draw in invited_draws:
        invite = QueueInvite(sender=user, receiver=receiver, draw=draw,
                             timestamp=int(time.time()))
        invite.save();

    sender_name = "%s %s (%s@princeton.edu)" % (user.firstname, user.lastname, user.netid)
    url = "http://dev.rooms.tigerapps.org:8099/manage_queues.html#received" #TODO - change this URL
    subject = "Rooms: Queue Invitation"
    message = """Your friend %s invited you to share a room draw queue on the
Princeton Room Draw Guide! Accept the request at the following URL: 

%s""" % (sender_name, url)
    notify(receiver, subject, message)

    return render_to_response('rooms/invite_queue.html')

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
        invite = user.q_received_set.get(pk=invite_id)
    except Exception as e:
        return HttpResponse(e)
    try:
        if accepted:
            queue = invite.accept()
            if not queue:
                return manage_queues(request)
            friends = queue.user_set.all()
            for friend in friends:
                if user != friend:
                    receiver_name = "%s %s (%s@princeton.edu)" % (user.firstname, user.lastname, user.netid)
                    subject = "Rooms: %s Joined Your Queue" % user.firstname
                    url = "http://rooms.tigerapps.org/"
                    message = """Your friend %s has joined your room draw queue! Visit %s to browse rooms
to add. """ % (receiver_name, url)
                    notify(friend, subject, message)
        else:
            invite.deny()
    except Exception as e:
        return HttpResponse(e)


    return manage_queues(request)

# Leave a queue that was previously shared
@login_required
def leave_queue(request):
    try:
        draw = Draw.objects.get(pk=int(request.POST['draw_id']))
    except:
        return HttpResponse('')
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    q1 = user.queues.get(draw=draw)
    if 1 == q1.user_set.count():
        return HttpResponse('')
    q2 = Queue.make(draw=draw, user=user)
    q2.save()
    qtrs = q1.queuetoroom_set.all()
    for qtr in qtrs:
        qtr.pk = None
        qtr.queue = q2
        qtr.save()
    user.queues.remove(q1)
    user.queues.add(q2)
    return manage_queues(request);
'''
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
                return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'form': form, 'submitted': False, 'edit': True})
            else:   
                form = ReviewForm()
                return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'form': form, 'submitted': False})
                
        #user asked to display current reviews
        elif display:
            revs = Review.objects.filter(room=room)
            print 'num reviews found: %d' % (len(revs))
            return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'reviews': revs, 'display': display})
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
                return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'submitted': True})
            else:
                form = ReviewForm()
                return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'form': form, 'submitted': True, 'error': 'Invalid submit data'})
        elif delete:
            if pastReview:
                pastReview.delete()
                return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'deleted': True})
        else:
            #someone's messing with the post params
            return HttpResponseRedirect(reverse(index))
    else:
        return render_to_response('rooms/reviewtest.html', {'roomid' : roomid, 'submitted': False})
'''
@login_required
def settings(request):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()

    return render_to_response('rooms/user_settings.html', {'user': user})

def handle_settings_form(request, user):
    
    
    if(request.POST['phone']):
        phone = int(request.POST['phone'])
    
        if (not user.phone) or (phone != int(user.phone)):
            # Send confirmation code
            carriers = Carrier.objects.order_by('name')
    
            for carrier in carriers:
                code = (phone / 10000) * 3 + user.id + carrier.id * 7
                content = "Your confirmation code is: %s" % code
                send_mail("", content, 'rooms@tigerapps.org',
                      ["%s@%s" % (phone, carrier.address)], fail_silently=False)
                user.confirmed = False

    user.phone = request.POST['phone']
    user.do_text = bool(('do_text' in request.POST) and request.POST['do_text'])
    user.do_email = bool(('do_email' in request.POST) and request.POST['do_email'])
    user.save()


def handle_confirmphone_form(confirmation, user):
    if ! user.phone:
        return False

    carrier_id = int(confirmation) - (int(user.phone) / 10000 * 3) - user.id;

    if carrier_id < 0 or carrier_id % 7 != 0:
        return False

    carrier_id /= 7

    try:
        carrier = Carrier.objects.get(id=carrier_id)
        user.carrier = carrier
        user.confirmed = True
        user.save()
        return True
    except:
        return False

 
@login_required
def confirm_phone(request):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if request.POST['form_type'] == 'settings':
            handle_settings_form(request, user)
            first_try = True
        elif request.POST['form_type'] == 'confirmphone':
            handle_confirmphone_form(request.POST['confirmation'], user)
            first_try = False
        else:
            first_try = True
    else:
        first_try = True

    return render_to_response('rooms/confirm_phone.html', {'user': user, 'first_try':first_try})


@login_required
def manage_queues(request, error=""):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()


    received_invites = QueueInvite.objects.filter(receiver=user)
    sent_invites = QueueInvite.objects.filter(sender=user)
    user_queues = user.queues.all()
    shared_queues = []
    for q in user_queues:
        if q.user_set.count() > 1:
            shared_queues.append(q)
    return render_to_response('rooms/manage_queues.html', {'user' : user,
                                                           'draws' : Draw.objects.all(),
                                                           'received_invites' : received_invites,
                                                           'sent_invites' : sent_invites,
                                                           'shared_queues' : shared_queues,
                                                           'error' : error })


def test(request):
    #return HttpResponse(testtime())
    externalResponse('Hello')
    return response

def trigger(request):
    print('Hello')    
    triggertime()
    return externalResponse('triggered')


#helper function
def notify(user, subject, message):
    if user.do_email:
        send_mail(subject, message, 'rooms@tigerapps.org',
                      ["%s@princeton.edu" % user.netid], fail_silently=False)
    if user.do_text and user.confirmed:
        send_mail(subject, message, 'rooms@tigerapps.org',
                      ["%s@%s" % (user.phone, user.carrier.address)], fail_silently=False)



