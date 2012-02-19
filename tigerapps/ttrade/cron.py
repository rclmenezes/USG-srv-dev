########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from django.core.mail import send_mail, BadHeaderError
from ttrade.models import *
from ttrade.emails import buyerConfirmation, listerConfirmation, expirationConfirmation
import datetime, sys

auctionList = Listing.objects.filter(method="Au", active=True, expire__lte=datetime.datetime.now())
for auction in auctionList:
    try:
        offer = auction.offers.get(price=auction.price)
        buyerConfirmation(auction, offer)
    except:
        offer = None
    print "Emailing " + auction.user.email
    listerConfirmation(auction, offer)
    auction.active = False
    auction.save()

expireList = Listing.objects.filter(expire__lte=datetime.datetime.now(), active=True)
for expire in expireList:
    expirationConfirmation(expire)
    expire.active = False
    expire.save()
    
print "Great success!"