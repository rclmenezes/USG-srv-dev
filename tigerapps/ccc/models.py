from django.db import models
from django.contrib.auth.models import User
import datetime

class Post(models.Model):
    title = models.CharField(max_length=40, unique=True, help_text="Title of the Post")
    content = models.TextField(help_text="Actual content, pure HTML")
    posted = models.DateTimeField(default=datetime.datetime.now(), help_text="Date posted")
    in_blog = models.BooleanField(default=True, help_text="If checked, this goes into the /blog page.")
    
    def __unicode__(self):
        return self.title

class LogCluster(models.Model):
    date_start = models.DateField(help_text="Date when service started")
    date_end = models.DateField(default=datetime.datetime.now(), help_text="Date when service ended")
    project = models.ForeignKey('ProjectOrOrganization', help_text="Project or organization the service was done with")
    hours = models.IntegerField(help_text="Total new hours since you last logged")
    user = models.ForeignKey(User, related_name="cluster_user")
    
    def __unicode__(self):
        return self.project.name
    
class ProjectRequest(models.Model):
    project = models.CharField(max_length=80)
    description = models.TextField(help_text='Description of activity')
    coordinator_name = models.CharField(max_length=40, help_text="Name of coordinator")
    coordinator_email = models.EmailField(help_text="Email of coordinator")
    user = models.ForeignKey(User, related_name="project_request_user")
    
    def __unicode__(self):
        return self.project
    
class ProjectOrOrganization(models.Model):
    name = models.CharField(max_length=80, unique=True, help_text="Name of Project or Organization")
    
    def __unicode__(self):
        return self.name

'''       
class Account(models.Model):
    user = models.ForeignKey(User, related_name="account_user")
    logs = models.ManyToManyField('LogCluster', null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username
        
    def get_hours(self):
        hours = 0
        for log in self.logs.filter(is_approved=True):
            hours += log.hours
        return hours
'''