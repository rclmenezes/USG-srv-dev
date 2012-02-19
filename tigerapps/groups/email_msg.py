from globalsettings import SITE_URL,SITE_EMAIL,ADMIN_EMAILS

GROUP_REQUEST_EMAIL = """There has been a request to create a new group profile on the Princeton Student Groups website:

Name: %s

Description: %s

You can contact the student who submitted this request at %s.

To process this request, please visit this link:

%sprocess/%s/

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
%s
""" % ('%s','%s','%s',SITE_URL,'%s',SITE_URL)

GROUP_REQUEST_ACK_EMAIL = """Your request to create a new group profile for "%s" on Princeton Student Groups has been submitted.  You will be notified by email when the request has been processed.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
%s
""" % ('%s',SITE_URL)

GROUP_REQUEST_REJECT_EMAIL = """Your request to create a new profile for "%s" on Princeton Student Groups has been denied.

If you believe this decision was in err, please contact the site administrator at %s.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
%s
""" % ('%s',ADMIN_EMAILS[0],SITE_URL)

GROUP_REQUEST_ACCEPT_EMAIL = """Your request to create a new group profile for "%s" on Princeton Student Groups has been accepted.  You can access the new profile at:

%sgroups/%s/

You have been granted officer status, meaning that you can edit group information, manage feeds/listservs, accept new members, and promote officers.  Please do not demote yourself unless you have appointed at least one other group officer.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

FEED_NOTIFICATION_EMAIL = """"%s" posted the following to its feed:

Title: %s

Post: %s

View this post at %sgroups/%s/feed/

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s','%s',SITE_URL,'%s',SITE_URL)

MESSAGE_NOTIFICATION_EMAIL = """"%s" posted the following to its message board:

Title: %s

Message: %s

View and comment on this message at %sgroups/%s/messages/%s

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s','%s',SITE_URL,'%s','%s',SITE_URL)


MSHIP_REQUEST_EMAIL = """There has been a new membership request to "%s" on Princeton Student Groups.

Student Name: %s

You can process this request at %sgroups/%s/approve/

Yours,
The Princeton Student Groups Team

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s',SITE_URL,'%s',SITE_URL)

MSHIP_REQUEST_ACCEPT_EMAIL = """Your membership request for "%s" has been approved on Princeton Student Groups.

You can access member features, such as email notification settings and the group message board, on the group profile:

%sgroups/%s/

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

MSHIP_REQUEST_REJECT_EMAIL = """Your membership request for "%s" has been rejected on Princeton Student Groups.  If you believe this decision was in error, please contact the officers of the group.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s',SITE_URL)

MSHIP_PROMOTE_EMAIL = """%s promoted you to an officer of "%s" on Princeton Student Groups.

You can access the group managment tools available to officers, including editing and communication privileges, on the group profile:

%sgroups/%s

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s',SITE_URL,'%s',SITE_URL)

MSHIP_PROMOTE_TITLE_EMAIL = """%s promoted you to an officer of "%s" on Princeton Student Groups.

Title: %s

You can access the group managment tools available to officers, including editing and communication privileges, on the group profile:

%sgroups/%s

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s','%s',SITE_URL,'%s',SITE_URL)

MSHIP_DEMOTE_EMAIL = """You have been demoted from officership in %s on Princeton Student Groups.  If you believe this was in err, please contact the group officers.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s',SITE_URL)

MSHIP_REMOVE_EMAIL = """You have been removed from %s on Princeton Student Groups.  If you believe this was in err, please contact the group officers.

If you wish to remain subscribed to the group, you can resubscribe on the group profile located at:

%sgroups/%s

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

MSHIP_LEAVE_EMAIL = """You have successfully left "%s" on Princeton Student Groups.

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s',SITE_URL)

MSHIP_STATUS_CHANGE_EMAIL = """You have successfully changed your status in "%s" on Princeton Student Groups.

Old Status: %s
New Status: %s

------------------------------------------------------------
This was an automated message from Princeton Student Groups. 
If you do not want to recieve these messages, please change 
your membership settings.
%s
""" % ('%s','%s','%s',SITE_URL)

INACTIVE_EMAIL = """NOTICE: The group "%s" on Princeton Student Groups has been marked as inactive.  If you would like to continue using the profile, please submit a reactivation request at:

%sgroups/%s/reactivate/

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

GROUP_RENEWAL_EMAIL = """Princeton student Groups requires that participating groups confirm their active status at the beginning of each year.

To confirm the active status of "%s", please visit the address:

%sgroups/%s/renew/

The deadline for renewing your group is September 15.

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

GROUP_RENEWAL_REMIND_EMAIL = """This is a reminder to renew your group's status on Princeton Student Groups no later than September 15.

Princeton student Groups requires that participating groups confirm their active status at the beginning of each year.

To confirm the active status of "%s", please visit the address:

%sgroups/%s/renew/

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

GROUP_RENEWAL_LAST_REMIND_EMAIL = """LAST REMINDER: Please renew the group "%s" on Princeton student Groups NO LATER THEN TOMORROW.  If the group is not renewed, it will be marked as inactive.

Princeton student Groups requires that participating groups confirm their active status at the beginning of each year.

To renew, please visit the address:

%sgroups/%s/renew/

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL,'%s',SITE_URL)

GROUP_REACTIVATE_REQUEST_EMAIL = """There has been a request to reactivate a group profile on the Princeton Student Groups website:

Name: %s

Description: %s

Reason: %s

You can contact the student who submitted this request at %s.

To process this request, please visit this link:

%sreactivate/%s/

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
"""%('%s','%s','%s','%s',SITE_URL,'%s',SITE_URL)

GROUP_REACTIVATE_ACK_EMAIL = """Your request to reactivate the profile for "%s" on Princeton Student Groups has been submitted.  You will be notified by email when the request has been processed.

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL,)

GROUP_REACTIVATE_REJECT_EMAIL = """Your request to reactivate the profile for "%s" on Princeton Student Groups has been denied.

If you believe this decision was in err, please contact the site administrator at %s.

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
"""%('%s',ADMIN_EMAILS[0],SITE_URL)

GROUP_REACTIVATE_ACCEPT_EMAIL = """Your request to reactivate the profile for "%s" on Princeton Student Groups has been accepted.

------------------------------------------------------------
This was an automated message from Princeton Student Groups.
%s
""" % ('%s',SITE_URL)
