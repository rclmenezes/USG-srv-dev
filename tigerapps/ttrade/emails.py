from django.core.mail import send_mail, BadHeaderError
from ttrade.models import *
import datetime

def listerConfirmation(listing, offer):
    if listing.method == 'Fi' or listing.method == 'Au':
        if offer is not None:
            subject = "[TigerTrade] Your listing has been purchased!"
            message = "Your listing, \"" + listing.title + "\", has been purchased for $" + str(offer.price)
            message += " by " + offer.user.email + "!\n\n"
        else:
            return expirationConfirmation(listing)
        
    elif listing.method == 'Fr':
        subject = "[TigerTrade] Your listing has been claimed!"
        message = "Your listing, \"" + listing.title + "\", has been claimed" 
        message += " by " + offer.user.email + "!\n\n"
    else:
        subject = "[TigerTrade] You have accepted an offer!"
        message = "You have accepted an offer for \"" + listing.title + "\""
        message += " by " + offer.user.email + "!\n\n"
    message += "You and the buyer are responsible for getting in contact. An email has also been sent to the buyer with your email.\n\n"   
    to_email = []
    to_email.append(listing.user.email)
    return sendMessage(subject, message, to_email)
        
def buyerConfirmation(listing, offer):
    if listing.method == 'Fi' or listing.method == 'Au':
        subject = "[TigerTrade] You have successfully purchased a listing!"
        message = "You have purchased the listing \"" + listing.title + "\" " + "for $" + str(offer.price) + "." 
        
    elif listing.method == 'Fr':
        subject = "[TigerTrade] You have successfully claimed a listing!"
        message = "You have claimed the listing \"" + listing.title + "\"." 

    else:
        subject = "[TigerTrade] Your offer has been accepted!"
        message = "Your offer for \"" + listing.title + "\" has been accepted. Your offer was: "
        if offer.price:
            message += "$" + offer.price
        else:
            message += "\n\n\"" + offer.additional + "\""
    message += "\n\nThe lister's email is " + listing.user.email + ". You and the lister are responsible for getting in contact. An email has also been sent to the lister.\n\n"
    to_email = []
    to_email.append(offer.user.email)
    return sendMessage(subject, message, to_email)
    
def offerListerConfirmation(listing, offer):
    subject = "[TigerTrade] An offer has been made for your listing!"
    message = "An offer has been made for \"" + listing.title + "\".\n\n"
    if offer.price:
        message += "Price offered: $" + str(offer.price) + "."
    else:
        message += "Offer: \"" + offer.additional + "\""
    message += "\n\nTo accept an offer, go to http://%sttrade.tigerapps.org/item/%s.\n\n" % (settings.CURRENT_HOST_PREFIX, str(listing.listingID))
    to_email = []
    to_email.append(listing.user.email)
    return sendMessage(subject, message, to_email)
    
def offerBuyerConfirmation(listing, offer):
    subject = "[TigerTrade] You have successfully made an offer!"
    message = "You have made an offer for \"" + listing.title + "\".\n\n"
    if offer.price:
        message += "Price offered: $" + str(offer.price) + "."
    else:
        message += "Offer: \"" + offer.additional + "\""
    message += "\n\nTo see the item again, go to http://%sttrade.tigerapps.org/item/%s. We'll let you know if it got accepted by the lister.\n\n" % (settings.CURRENT_HOST_PREFIX, str(listing.listingID))
    from_email = "DO_NOT_REPLY@tigerapps.org"
    to_email = []
    to_email.append(offer.user.email)
    return sendMessage(subject, message, to_email)
    
def offerRejection(listing, offer):
    subject = "[TigerTrade] Your offer has been rejected"
    message = "Your offer for \"" + listing.title + "\" has been rejected.\n\n"
    if offer.price:
        message += "Price offered: $" + str(offer.price) + "."
    else:
        message += "Offer: \"" + offer.additional + "\""
    message += "\n\nTo see the item again and make another offer, go to http://%sttrade.tigerapps.org/item/%s. Better luck next time!\n\n" % (settings.CURRENT_HOST_PREFIX, str(listing.listingID))
    from_email = "DO_NOT_REPLY@tigerapps.org"
    to_email = []
    to_email.append(offer.user.email)
    return sendMessage(subject, message, to_email)
    
def expirationConfirmation(listing):
    subject = "[TigerTrade] Your listing has expired!"
    if listing.offers.all():
        message = "To see your offers, go to http://%sttrade.tigerapps.org/item/%s.\n\n" % (settings.CURRENT_HOST_PREFIX, str(listing.listingID))
    else:
        message = "You have received any offers :(. Maybe you should try renewing the expiration of your listing and changing it at http://%sttrade.tigerapps.org/item/%s.\n\n" % (settings.CURRENT_HOST_PREFIX, str(listing.listingID))
    to_email = []
    to_email.append(listing.user.email)
    return sendMessage(subject, message, to_email)
    
def sendMessage(subject, message, to_email):
    from_email = "DO_NOT_REPLY@tigerapps.org"
    message += "Thanks,\nThe TigerTrade Team.\n\n(Please note that the USG and TigerTrade and not responsible for any inappropriate content made by our users. To register a complaint about another user or to report a bug, please send an email to it@princetonusg.com)"
    try:
       send_mail(subject, message, from_email, to_email)
    except BadHeaderError:
       pass
    return True
