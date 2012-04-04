from django.db import models
from stdimage import StdImageField
import datetime
    
class Office(models.Model):
    name = models.CharField(max_length=50)
    freshman_eligible = models.BooleanField("Freshman Eligible")
    sophomore_eligible = models.BooleanField("Sophomore Eligible")
    junior_eligible = models.BooleanField("Junior Eligible")
    freshman_vote = models.BooleanField("Freshman Vote")
    sophomore_vote = models.BooleanField("Sophomore Vote")
    junior_vote = models.BooleanField("Junior Vote")
    senior_vote = models.BooleanField("Senior Vote")
    
    def __unicode__(self):
        return self.name
    
class Candidate(models.Model):
    netid = models.CharField("NetID", max_length=8)
    YEAR_CHOICES = (
        (u'FR', u'FRESHMAN'),
        (u'SO', u'SOPHOMORE'),
        (u'JU', u'JUNIOR'),
        (u'SE', u'SENIOR')
    )
    year = models.CharField(max_length=3, choices=YEAR_CHOICES)
    office = models.ForeignKey(Office)
    name = models.CharField(verbose_name="Name as it will appear on the ballot", max_length=45)
    statement = models.TextField("Statement (max 120 words)")
    headshot = StdImageField("Headshot", upload_to='elections/upload/', size=(350,225), thumbnail_size=(125, 350))
    election = models.ForeignKey('Election', related_name='election')
    
    def __unicode__(self):
        return self.name
    
class Election(models.Model):
    electionID = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=50)
    offices = models.ManyToManyField(Office)
    deadline = models.DateTimeField("Statement Deadline")
    start = models.DateTimeField("Election Start")
    end = models.DateTimeField("Election End")
    
    def __unicode__(self):
        return self.name
        
class Runoff(models.Model):
    election = models.ForeignKey('Election', related_name='runoff_election')
    candidates = models.ManyToManyField('Candidate', related_name='candidate')
    
    def __unicode__(self):
        return self.election.name + " Runoff"
