from django.core.management import setup_environ
from DVD import settings
from django.core.mail import send_mail, BadHeaderError
from dvdapp.models import *

def reminder():
    subject = "[USG DVD]  is now available!"
    message = "There is a copy of now available in the USG Office.\nThanks,\nThe USG"
    from_email = "DO_NOT_REPLY@tigerapps.org"
    
    to_email = []
    to_email.append("atrippe@princeton.edu")
        
    try:
        send_mail(subject, message, from_email, to_email)
    except BadHeaderError:
        pass