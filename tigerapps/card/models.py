# -------------------------------------------------------------------#
# models.py                                                          #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: Defines the data structures to store in the database. #
# Note that upon failure, these functions will return exceptions.    #
# -------------------------------------------------------------------#

from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Define choices for access and meal_type categories
ACCESS_CHOICES = (
    ('M', 'Member'),
    ('C', 'Checker'),)
MEAL_CHOICES = ('Dinner', 'Lunch', 'Breakfast',
                'Brunch', 'Other', )

MEAL_TUPLE_CHOICES = (('Dinner','Dinner'), 
                ('Lunch','Lunch'),
                ('Breakfast','Breakfast'),
                ('Brunch','Brunch'),
                ('Other','Other' )
)

# Create your models here.
class Club(models.Model):
    name = models.CharField(max_length=20, unique=True) #club name, capitalized
    account = models.OneToOneField(User, related_name='account', null=True, blank=True) #account for club functions
    check = models.ForeignKey('Member', related_name='check', null=True, blank=True) # special checker object for adding meals

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.account: # automatically create account
            name = self.name.replace(' ', '').lower()
            self.account = User.objects.create_user(name, '%s@princeton.edu'%name, name)
            self.account.is_staff = False
            self.account.save()
        if not self.check: # automatically create checker
            n = str(self.account.username).lower() + 'check'
            self.check = Member(netid=n, first_name='x', last_name='x', puid=self.account.id, year=self.account.id, access='A')
            self.check.save()
        super(Club, self).save(*args, **kwargs)
        self.check.club=self
        self.check.save()

    class Meta:
        db_table = 'card_clubs'
        ordering = ['name']
        
class Member(models.Model):
    netid = models.CharField(max_length=30, primary_key=True, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    puid = models.PositiveIntegerField(unique=True)
    year = models.PositiveIntegerField()
    club = models.ForeignKey('Club', null=True, blank=True)
    access = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='M')
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.netid

    def create_email(self):
        return str(self.netid)+'@princeton.edu'
    email = property(create_email)

    def full_name(self):
        return str(self.first_name) + ' ' + str(self.last_name)
    full_name = property(full_name)
    
    def validate(self):  # validate that member object is correct
        errmes = None
        
        # default club checker account; not subject to validation
        if str(self.netid).count('check') > 0 and self.first_name=='x' and self.last_name=='x': # insecure
            return errmes

        # Date
        now = date.today()
        if len(str(self.year)) != 4 or int(self.year) < int(now.year):
            errmes = 'Error: %s: year must be year of future graduation in yyyy format' % (self.netid,)
        # Netid
        elif not self.netid.islower() or not self.netid.isalnum(): #self.netid.isalpha():
            errmes =  'Error: %s: invalid netid format' % (self.netid,)
        # Puid
        elif len(str(self.puid)) != 9:
            errmes = 'Error: %s: invalid PUID format' % (self.netid,)
        return errmes

    def save(self, *args, **kwargs):
        errmes = self.validate()
        if errmes:
            raise Exception(errmes)
        else:
            super(Member, self).save(*args, **kwargs)

    class Meta:
        ordering = ['last_name']
        db_table = 'card_members'

class Exchange(models.Model):
    meal_1 = models.ForeignKey('Meal', related_name='meal_1')
    meal_2 = models.ForeignKey('Meal', null=True, blank=True, related_name='meal_2')  # if None, exchange is incomplete


    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.meal_1 == self.meal_2:
            raise Exception('Error: meals in an exchange must be distinct')
        else:
            super(Exchange, self).save(*args, **kwargs)

    class Meta:
        db_table = 'card_exchanges'
        ordering = ['meal_1']

class Meal(models.Model):
    host = models.ForeignKey('Member', related_name='host')
    guest = models.ForeignKey('Member', related_name='guest')
    checker = models.ForeignKey('Member', related_name='checker')
    date = models.DateField(default=date.today())
    meal_type = models.CharField(max_length=10, default='Dinner') #choices=MEAL_TUPLE_CHOICES,default='D') 

    def __unicode__(self):
        return '%s'%self.date    

    # Deprecated; implemented in checksession.py
    # TODO: exchange association for admin account
    def create_exchange(self):
        h = self.host
        g = self.guest
        try:
            ex = Exchange.objects.get(meal_2__isnull=True, meal_1__host=g, meal_1__guest=h)
            ex.meal_2 = self
            ex.save()
            return ex
        except Exception, e:
            print e
            ex = Exchange()
            ex.meal_1 = self
            ex.save()
            return ex
    
    def save(self, *args, **kwargs):
        if self.host.club != self.checker.club:
            raise Exception('Error: checker club and host club do not match')
        elif self.host.club == self.guest.club:
            raise Exception('Error: guest and host should not be from the same club')
        elif self.checker.access != 'C' and self.checker.access != 'A':
            raise Exception('Error: checker not authorized to enter meal')
        elif self.meal_type not in MEAL_CHOICES:
            raise Exception('Error: not a valid meal type.')
        else:
            super(Meal, self).save(*args, **kwargs)
            #self.create_exchange()

    class Meta:
        ordering = ['-date']
        db_table = 'card_meals'

