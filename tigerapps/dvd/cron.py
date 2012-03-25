from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.core.mail import send_mail, BadHeaderError
from dvdapp.models import *
import datetime, sys

def reminder():
    if settings.REMINDER_EMAILS:
        now = datetime.datetime.now()
        rentalList = Rental.objects.filter(dateReturned=None).filter(dateDue__lte=now)
        
        subject = "[USG DVD] Reminder"
        from_email = "DO_NOT_REPLY@tigerapps.org"
        to_email = []
        for rental in rentalList:
            message = "Your rental of " + rental.dvd.name + " was due on " + str(rental.dateDue) + ". Please return it as soon as you can.\nThanks,\nThe USG"
            to_email.append(rental.netid + "@princeton.edu")
            
        try:
            send_mail(subject, message, from_email, to_email)
        except BadHeaderError:
            send_mail("USG DVD email error", "Notification to " + rental.netid " has failed.", "DO_NOT_REPLY@tigerapps.org", ['rod333@gmail.com'])
            
reminder()