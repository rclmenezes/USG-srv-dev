from globalsettings import SITE_URL,SITE_EMAIL,ADMIN_EMAILS,EMAIL_HEADER_PREFIX
from django.core.mail import send_mail
from models import *
from django.contrib import admin
from forms import *
from email_msg import *
from datetime import date
from adminsites import groupsAdmin

# Membership admin
class GroupMembershipInline(admin.TabularInline):
    model = Membership
    exclude = ('officer_order','has_order','display','feed_notifications','message_notifications','mship_notifications','request_notifications')
    raw_id_fields = ('student','group')
    formset = MembershipAdminFormSet
    extra = 3
    template = '/srv/tigerapps/templates/groups/admin/group_mship_inline.html'

class StudentMembershipInline(admin.TabularInline):
    model = Membership
    exclude = ('officer_order','has_order','display','feed_notifications','message_notifications','mship_notifications','request_notifications')
    extra = 3

# Student admin
class StudentAdmin(admin.ModelAdmin):
    inlines = (StudentMembershipInline,)
    list_display = ('last_name','first_name','netid','email','year')
    search_fields = ('last_name','first_name','netid')
    list_filter = ('year',)

# Group admin
def mark_active(modeladmin, request, queryset):
    queryset.update(active_status='A')
mark_active.short_description = 'Mark groups as active'

def mark_inactive(modeladmin, request, queryset):
    for g in queryset:
        if g.active_status != 'I':
            g.active_status = 'I'
            g.date_last_active = date.today()
            g.save()
            list = []
            officers = Membership.objects.filter(group=g,type='O')
            for o in officers:
                list.append(o.student.email)
                send_mail(EMAIL_HEADER_PREFIX+'%s Deactivated'%g.name, INACTIVE_EMAIL % (g.name,g.url), SITE_EMAIL, list, fail_silently=False)
#    queryset.update(active_status='I')
mark_inactive.short_description = 'Mark groups as inactive'

def mark_renew(modeladmin, request, queryset):
    queryset.update(active_status='R')
    for group in queryset:
        list = []
        officers = Membership.objects.filter(group=group,type='O')
        for o in officers:
            list.append(o.student.email)
        send_mail(EMAIL_HEADER_PREFIX+'Renew %s Profile'%group.name, GROUP_RENEWAL_EMAIL % (group.name,group.url), SITE_EMAIL, list, fail_silently=False)
mark_renew.short_description = 'Mark groups as up for renewal'

class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupMembershipInline,)
    exclude = ('sort_letter','sort_name','ticket')
    list_display = ('name','active_status','date_last_active','last_update')
    search_fields = ('name',)
    list_filter = ('active_status','date_last_active')
    actions = [mark_active, mark_inactive, mark_renew]

# Entry admin
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title','pub_date','group','event')
    exclude = ('pub_date','group')
    search_fields = ('title','group__name')
    list_filter = ('pub_date',)
#    form = EntryForm

# reactivation, register requests
def reactivation_approve(modeladmin, request, queryset):
    for g in queryset:
        g.group.active_status = 'A'
        send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Profile Reactivated'%g.group.name, GROUP_REACTIVATE_ACCEPT_EMAIL % g.group.name, SITE_EMAIL, [g.supplicant.email], fail_silently=False)
        g.delete()
reactivation_approve.short_description = 'Approve request'

def reactivation_reject(modeladmin, request, queryset):
    for g in queryset:
        send_mail(EMAIL_HEADER_PREFIX+'Reactivation Request Rejected for \"%s\"'%g.group.name, GROUP_REACTIVATE_REJECT_EMAIL % (g.group.name,), SITE_EMAIL, [g.supplicant.email], fail_silently=False)
        g.delete()
reactivation_reject.short_description = 'Reject request'

def group_request_approve(modeladmin, request, queryset):
    for g in queryset:
        new = g.make_group()
        send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Profile Created'%new.name, GROUP_REQUEST_ACCEPT_EMAIL % (new.name, new.url), SITE_EMAIL, [g.supplicant.email], fail_silently=False)
        g.delete()
group_request_approve.short_description = 'Approve request'

def group_request_reject(modeladmin, request, queryset):
    for g in queryset:
        send_mail(EMAIL_HEADER_PREFIX+'New Group Request Rejected for \"%s\"'%g.name, GROUP_REQUEST_REJECT_EMAIL % (g.name,), SITE_EMAIL, [g.supplicant.email], fail_silently=False)
        g.delete()
group_request_reject.short_description = 'Reject request'


class GroupReactivationAdmin(admin.ModelAdmin):
    list_display = ('group','supplicant','ticket',)
    actions = [reactivation_approve,reactivation_reject]
    search_fields = ('group__name',)
class GroupRequestAdmin(admin.ModelAdmin):
    list_display = ('name','supplicant','ticket',)
    actions = [group_request_approve,group_request_reject]
    search_fields = ('group__name',)

# membership requests
def request_approve(modeladmin, request, queryset):
    for mship in queryset:
        mship.make_member()
        if mship.notify_me:
            send_mail(EMAIL_HEADER_PREFIX+'Membership Request to \"%s\" Approved'%mship.group.name, MSHIP_REQUEST_ACCEPT_EMAIL % (mship.group.name,mship.group.url), SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
        mship.delete()
request_approve.short_description = 'Approve request'

def request_reject(modeladmin, request, queryset):
    for mship in queryset:
        if mship.notify_me:
            send_mail(EMAIL_HEADER_PREFIX+'Membership Request to \"%s\" Denied'%mship.group.name, MSHIP_REQUEST_REJECT_EMAIL % mship.group.name, SITE_EMAIL, [str(mship.student.email)], fail_silently=False)
        mship.delete()
request_reject.short_description = 'Reject request'

class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('id','group','student')
    fields = ('student','group')
    search_fields = ('student__first_name','student__last_name','student__netid','group__name')
    actions = [request_approve,request_reject]

# Register admins
groupsAdmin.register(Student, StudentAdmin)
groupsAdmin.register(Group, GroupAdmin)
groupsAdmin.register(Entry, EntryAdmin)
groupsAdmin.register(Category)
groupsAdmin.register(GroupRequest, GroupRequestAdmin)
groupsAdmin.register(MembershipRequest, MembershipRequestAdmin)
groupsAdmin.register(GroupReactivationRequest, GroupReactivationAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Category)
admin.site.register(GroupRequest, GroupRequestAdmin)
admin.site.register(MembershipRequest, MembershipRequestAdmin)
admin.site.register(GroupReactivationRequest, GroupReactivationAdmin)
