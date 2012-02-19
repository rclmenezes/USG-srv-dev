################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  usermsg.py
# Info :  a messaging framework, either for a visitor (top msg) or
#		  a user (profile msg)
################################################################

from datetime import datetime
from models import VisitorMessage, UserMessage

# Message types
# 0: Error
# 1: Message
# 2: Tip
# 3: Sticky
# 
class MsgMgr:
	
	@staticmethod
	def push(request, msg_body = '', msg_type = 1, msg_show = datetime.now(), msg_to_page = None):
		""" Push a message to be displayed at a later time """
		msg = VisitorMessage(
					vm_session = request.session.session_key,
					vm_date_queued = datetime.now(),
					vm_show_after = msg_show,
					vm_from_page = request.path,
					vm_to_page = msg_to_page,
					vm_class = msg_type,
					vm_contents = msg_body,
					vm_pending = True)
		
		msg.save()
	
	@staticmethod
	def iterable(request):
		""" Get messages to be displayed """
		try:
			qs1 = VisitorMessage.objects.filter(vm_pending = True, vm_session = request.session.session_key, vm_show_after__lte = datetime.now(), vm_to_page = None)
			qs2 = VisitorMessage.objects.filter(vm_pending = True, vm_session = request.session.session_key, vm_show_after__lte = datetime.now(), vm_to_page = request.path)
			qs = qs1 | qs2
			for msg in qs:
				msg.deactivate()
			return qs
		except:
			return None
	
	@staticmethod
	def sendmsg(user, message):
		""" Send a User Message to the user """
		msg = UserMessage(um_user = user, um_contents = message)
		msg.save()

class Msg:
	
	def __init__(self, msg_body = '', msg_type = 1):
		self.type = msg_type
		self.contents = msg_body
	
	def push(self, request, dest_page = None):
		MsgMgr.push(request = request, msg_body = self.contents, msg_type = self.type, msg_to_page = dest_page)
		
