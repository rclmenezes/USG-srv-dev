from django.core.mail import send_mail, BadHeaderError

def sendNotice(noticeList, dvd):
    subject = "[USG DVD] " + dvd.name + " is now available!"
    message = "There is a copy of " + dvd.name + " now available in the USG Office.\nThanks,\nThe USG"
    from_email = "DO_NOT_REPLY@tigerapps.org"
    
    to_email = []
    for notice in noticeList:
        to_email.append(notice.netid + "@princeton.edu")
        
    try:
        send_mail(subject, message, from_email, to_email)
    except BadHeaderError:
        pass