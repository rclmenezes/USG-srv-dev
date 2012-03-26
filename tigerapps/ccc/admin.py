from models import *
from django.contrib import admin
from django.db import IntegrityError
from django.core.mail import send_mail

class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'content', 'in_blog']})
    ]
    list_display = ('title',)
    search_fields = ['title', 'content']
    
class LogClusterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['date_start', 'date_end', 'project', 'hours', 'year', 'res_college', 'eating_club']})
    ]
    list_display = ('user', 'project', 'date_start', 'hours')
    search_fields = ['user__username']
            
class ProjectRequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'project', 'description', 'coordinator_name', 'coordinator_email']})
    ]
    list_display = ('project', 'user')
    search_fields = ['project']
    actions = ['approve_project']
    
    def approve_project(self, request, queryset):
        message_bit = ""
        approved = 0
        for project_request in queryset:
            try:
                project = ProjectOrOrganization(name=project_request.project) # Wow, these names got out of hand.
                project.save()
                email = project_request.user.username + "@princeton.edu"
                project_request.delete()
                approved += 1
                send_mail('[CCC] Your project has been approved!', 
                          'Hi,\n\nYour project, ' + project.name + ', has been approved. You can now log your hours of service on the CCC site at http://ccc.tigerapps.org/log.\n\nBest,\n\nThe CCC Staff', 
                          'do-not-reply@tigerapps.org',
                           [email], 
                           fail_silently=True)
            except IntegrityError:
                message_bit = "There's already a project called " + project.name + ". "
                
        if approved == 1:
            message_bit += "1 project was approved."
        else:
            message_bit += "%s stories were approved." % approved
        
        self.message_user(request, message_bit)
        
    approve_project.short_description = "Approve project or organization"
 
admin.site.register(Post, PostAdmin)
admin.site.register(LogCluster, LogClusterAdmin)
admin.site.register(ProjectRequest, ProjectRequestAdmin)
admin.site.register(ProjectOrOrganization)

