################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  rsvp.py
# Info :  utilities for sending/responding to invitations
################################################################

from models import *
from cauth import *
from calmailer import *
from mailer import *
from usermsg import Msg, MsgMgr

def send_message(sender,cluster,title,body):
	""" Post a board message """
	if sender and cluster and title and body:
		message = BoardMessage(	boardmessage_eventcluster = cluster,
								boardmessage_title = title,
								boardmessage_poster = sender,
								boardmessage_text = body)
		message.save()
		notify_other_posters(message)
		return Msg('You\'ve successfully posted a message to the discussion board.')

def notify_other_posters(message):
	""" Notify other users who posted on a message board previously that there's a new post """
	cluster = message.boardmessage_eventcluster
	messages = BoardMessage.objects.filter(boardmessage_eventcluster = cluster)
	posters = []
	for msg in messages:
		posters.append(msg.boardmessage_poster)
	posterset = set(posters)
	for usr in posterset:
		if usr != message.boardmessage_poster:
			MsgMgr.sendmsg(usr,'%s has just posted a reply to "%s."' % (message.boardmessage_poster.full_name(),cluster.cluster_title))
		

def send_invite(sender,recipient,event):
	""" Send an invitation to a user """
	if sender and recipient and event:
		try:
			dup = RSVP.objects.get(rsvp_user = recipient, rsvp_event = event)
		except:
			dup = None
		if dup == None:
			invite = RSVP(	rsvp_user = recipient, 
							rsvp_event = event,
							rsvp_referrer = sender,
							rsvp_reminder_enabled = False,
							rsvp_type = 'Pending')
			invite.save()
			email_invite(recipient, sender, event, invite)
			MsgMgr.sendmsg(recipient,'%s just invited you to %s' % (sender.full_name(),event.displayname()))
			if sender == recipient:
				return Msg('You\'ve successfully sent an invitation to yourself. Lonely, huh?',1)
			else:
				return Msg('You\'ve successfully sent an invitation to %s.' % (recipient.casual_name()),1)
		elif dup.rsvp_referrer == sender:
			return Msg('''You have already sent an identical invitation to %s.''' % (recipient.casual_name()),0)
		elif dup.rsvp_referrer != sender:
			if dup.rsvp_type == 'Accepted':
				return Msg('''%s is already going to this event. No new invitation was sent.''' % (recipient.casual_name()),0)
			else:
				return Msg('''Someone else has already invited %s to this event. No new invitation was sent.''' % (recipient.casual_name()),0)
				
	else:
		return Msg('Malformed invitation.',0)

def accept_invitation(invite):
	""" Accept an invitation """
	if invite.rsvp_referrer != None:
		if invite.rsvp_type != 'Accepted':
			if invite.rsvp_event.deadlineOkay():
				if invite.rsvp_event.moreOkay():
					invite.rsvp_type = 'Accepted'
					invite.rsvp_reminder_enabled = True
					invite.rsvp_event.event_attendee_count = invite.rsvp_event.event_attendee_count + 1
					invite.rsvp_event.save()
					invite.save()
					MsgMgr.sendmsg(invite.rsvp_referrer,'%s has accepted your invitation to \'%s.\'' % (invite.rsvp_user.full_name(), invite.rsvp_event.displayname()))
					return Msg('You\'ve accepted %s\'s invitation.' % (invite.rsvp_referrer.casual_name()),1)
				else:
					return Msg('We\'re sorry, but the maximum attendance for this event has been reached.',0)					
			else:
				return Msg('We\'re sorry, but the deadline for confirming attendance to this event has passed.',0)	
		else:
			return Msg('You\'ve already accepted %s\'s invitation.' % (invite.rsvp_referrer.casual_name()),2)
	else:
		return Msg('You can\'t accept an invitation without a sender.',0)


def decline_invitation(invite):
	""" Decline an invitation """
	if invite.rsvp_type != 'Declined' and invite.rsvp_referrer != None:
		invite.rsvp_type = 'Declined'
		invite.save()
		return Msg('You\'ve declined %s\'s invitation.' % (invite.rsvp_referrer.casual_name()),1)
	else:
		return Msg('That invitation cannot be declined. You may have already declined it.',1)
		

def confirm_attendance(user,referrer,event,reminder):
	""" Add an event to the user's calendar """
	try:
		rsvpdup = RSVP.objects.get(rsvp_user = user, rsvp_event=event)
		if rsvpdup.rsvp_type == 'Accepted':
			return Msg('''This event is already on your personal calendar! You can't add it twice.''' % (),0)
		elif (rsvpdup.rsvp_type == 'Pending' or rsvpdup.rsvp_type == 'Declined') and rsvpdup.rsvp_referrer:
			return accept_invitation(rsvpdup)
		else:
			return Msg('''You cannot add this event at this time; there was an internal error.''' % (),0)
	except:
		if event.deadlineOkay():
			if event.moreOkay():
				confirm = RSVP(	rsvp_user = user, 
								rsvp_event = event,
								rsvp_referrer = referrer,
								rsvp_reminder_enabled = reminder,
								rsvp_type = 'Accepted')
				event.event_attendee_count = event.event_attendee_count + 1
				event.save()
				confirm.save()
				return Msg('''You've added '%s' to <a href="/user/events">your calendar</a>.''' % (event.displayname()),1)
			else:
				return Msg('We\'re sorry, but the maximum attendance for this event has been reached.',0)
		else:
			return Msg('We\'re sorry, but the deadline for confirming attendance to this event has passed.',0)
	
	
def unconfirm_attendance(user,event):
	""" Remove an event from the user's calendar """
	try:
		confirmation = RSVP.objects.get(rsvp_user = user, rsvp_event = event)
		if confirmation.rsvp_referrer == None:
			confirmation.delete()
			event.event_attendee_count = event.event_attendee_count - 1
			event.save()			
			return Msg(''''%s' has been removed from <a href="/user/events">your calendar</a>.''' % (event.displayname()),2)	
		else:
			if confirmation.rsvp_type == 'Accepted':
				confirmation.rsvp_type = 'Declined'
				confirmation.save()
				event.event_attendee_count = event.event_attendee_count - 1
				event.save()				
				return Msg(''''%s' has been removed from <a href="/user/events">your calendar</a>. The invitation from %s has been changed to 'declined.' ''' % (event.displayname(), confirmation.rsvp_referrer.full_name()),2)
			elif confirmation.rsvp_type == 'Declined':
				return Msg('It seems that you have already declined an invitation to this event.',0)
			elif confirmation.rsvp_type == 'Pending':
				return decline_invitation(confirmation)
			else:
				return Msg('''There was a problem processing this request. The status of your invitation to this event could not be determined.''',0)
	except:
		return Msg('''There was a problem processing this request.''',0)
	
