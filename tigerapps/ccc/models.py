from django.db import models
from django.contrib.auth.models import User
import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta

YEAR_CHOICES = (("2012", "2012"), ("2013", "2013"), ("2014", "2014"), ("2015", "2015"))
RES_COLLEGE_CHOICES = (("Forbes","Forbes"), ("Whitman", "Whitman" ), ("Rockefeller", "Rockefeller"),
                       ("Mathey", "Mathey"), ("Wilson", "Wilson"), ("Butler", "Butler"))
EATING_CLUB_CHOICES = (("Cannon","Cannon"), ("Cap and Gown","Cap and Gown"), ("Tower","Tower"),
                       ("Ivy","Ivy"), ("Tiger Inn","Tiger Inn"), ("Cottage","Cottage"),
                       ("Cloister","Cloister"), ("Charter","Charter"), ("Colonial","Colonial"),
                       ("Quadrangle","Quadrangle"), ("Terrace","Terrace"))


class Post(models.Model):
    title = models.CharField(max_length=40, unique=True, help_text="Title of the Post")
    content = models.TextField(help_text="Actual content, pure HTML")
    posted = models.DateTimeField(default=datetime.datetime.now(), help_text="Date posted")
    in_blog = models.BooleanField(default=True, help_text="If checked, this goes into the /blog page.")
    
    def __unicode__(self):
        return self.title


class GroupHoursManager(models.Manager):
    def get_months(self):
        '''ready for sending to <select> html box'''
        months = sorted(list(set(g.month for g in GroupHours.objects.all())))
        return months

#I made this so the leaderboard would be more efficient 
class GroupHours(models.Model):
    group = models.CharField(max_length=30)
    hours = models.IntegerField()
    month = models.DateField()

    objects = GroupHoursManager()
    
    def __unicode__(self):
        return self.group

    class Meta:
        ordering = ['month']
        verbose_name_plural = 'Group hours'



class LogClusterManager(models.Manager):
    def get_user_hours(self, user):
        hours = LogCluster.objects.filter(user=user).aggregate(models.Sum('hours'))['hours__sum']
        if not hours:
            return 0
        return hours

    def get_month_hours(self, month, group=None, group_type=None):
        next_month = month + relativedelta(months=+1)
        qset = LogCluster.objects.filter(date__gte=month, date__lt=next_month)
        if group:
            qset = qset.filter(**{group_type:group})
        results = qset.values('user__username').annotate(tot_hours=models.Sum('hours'))
        top_hours = sorted([(res['user__username'], res['tot_hours']) for res in results], key=itemgetter(1), reverse=True)
        return top_hours


class LogCluster(models.Model):
    date = models.DateField(help_text="Date of service")
    #date_end = models.DateField(default=datetime.datetime.now(), help_text="Date when service ended")
    project = models.ForeignKey('ProjectOrOrganization', help_text="Project or organization the service was done with")
    hours = models.IntegerField(help_text="Total new hours since you last logged")
    year = models.CharField(max_length=4, choices=YEAR_CHOICES, blank=True, null=True)
    res_college = models.CharField("Residential College", max_length=20, choices=RES_COLLEGE_CHOICES, blank=True, null=True)
    eating_club = models.CharField(max_length=30, choices=EATING_CLUB_CHOICES, blank=True, null=True)
    user = models.ForeignKey(User, related_name="logcluster")
    
    objects = LogClusterManager()
    
    def __unicode__(self):
        return self.project.name

class Award(models.Model):
    date = models.DateField(help_text="Date award given")
    user = models.ForeignKey(User, related_name="award")
    hours = models.IntegerField(help_text="Number of hours that triggered award")

    def __unicode__(self):
        return "%d: %s (%s)" % (self.award_level, self.user.username, self.date.strftime("%B %d, %Y"))

class ProjectRequest(models.Model):
    project = models.CharField(max_length=80)
    description = models.TextField(help_text='Description of activity')
    coordinator_name = models.CharField(max_length=40, help_text="Name of coordinator")
    coordinator_email = models.EmailField(help_text="Email of coordinator")
    user = models.ForeignKey(User, related_name="projectrequest")
    
    def __unicode__(self):
        return self.project
    
class ProjectOrOrganization(models.Model):
    name = models.CharField(max_length=80, unique=True, help_text="Name of Project or Organization")

    class Meta:
        ordering = ['name']
    
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
