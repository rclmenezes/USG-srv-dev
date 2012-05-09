from django.db import models
from django.forms import ModelForm

photopath = 'photo'

class Draw(models.Model):
    name = models.CharField(max_length=24)

    def __unicode__(self):
        return self.name

# campus buildings    
class Building(models.Model):
    name = models.CharField(max_length=30)
    pdfname = models.CharField(max_length=30)
    availname = models.CharField(max_length=30)
    draw = models.ManyToManyField('Draw')
    lat = models.FloatField()
    lon = models.FloatField()

    def __unicode__(self):
        return self.name

# door rooms
class Room(models.Model):
    
    GENDER_CHOICES = (
        ('E', 'Either'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Mixed')
	)
    
    BATHROOM_CHOICES = (
        ('PU', 'Public'),
        ('PR', 'Private'),
        ('SH', 'Shared')
	)
	
    RATINGS = ( (i, i) for i in range(6) )

	# room numbers can include letters
    number = models.CharField(max_length=10)
    sqft = models.IntegerField()
    occ = models.IntegerField()
    building = models.ForeignKey('Building')
    subfree = models.BooleanField()
    numrooms = models.IntegerField()
    floor = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    avail = models.BooleanField()
    adjacent = models.CharField(max_length=10)
    # ADA accessible
    ada = models.BooleanField()
    # bi-level room
    bi = models.BooleanField();
    # connecting single
    con = models.BooleanField();
    bathroom = models.CharField(max_length=2, choices=BATHROOM_CHOICES)
    
    def __unicode__(self):
        return "%s %s" % (self.building.name, self.number)

# users
class User(models.Model):
    netid = models.CharField(max_length=30)
    firstname = models.CharField('First Name', max_length=45, null=True, blank=True) # givenName
    lastname = models.CharField('Last Name', max_length=45, null=True, blank=True) # sn
    pustatus = models.CharField(max_length=20, null=True, blank=True) # undergraduate or graduate
    puclassyear = models.IntegerField('Class Year', null=True, blank=True) # puclassyear
    queues = models.ManyToManyField('Queue')
    do_email = models.BooleanField(default=True)
    phone = models.CharField(max_length=12, blank=True)
    do_text = models.BooleanField(default=False)
    carrier = models.ForeignKey('Carrier', null=True)
    confirmed = models.BooleanField('Confirmed', default=False) #whether or not has confirmed phone number

    def __unicode__(self):
        return self.netid

# queues
class Queue(models.Model):
    draw = models.ForeignKey('Draw')
    def __unicode__(self):
        return self.draw.name

# queue-to-room mappings
class QueueToRoom(models.Model):
    queue = models.ForeignKey('Queue')
    room = models.ForeignKey('Room')
    ranking = models.IntegerField()

UPDATE_KINDS = (
    (0, 'edit'),
    (1, 'merge'),
)

# An update to a queue
class QueueUpdate(models.Model):
    queue = models.ForeignKey('Queue')
    timestamp = models.IntegerField()
    kind = models.IntegerField(choices=UPDATE_KINDS) #either edit or merge
    kind_id = models.IntegerField() # If merge, new queue id, otherwise edit user id

# An invitation to a the queue owned by a user
class QueueInvite(models.Model):
    sender = models.ForeignKey('User', related_name='q_sent_set')
    receiver = models.ForeignKey('User', related_name='q_received_set')
    draw = models.ForeignKey('Draw')
    # UNIX timestamp
    timestamp = models.IntegerField()

    def __unicode__(self):
        return "%s->%s %s" % (self.sender.netid, self.receiver.netid, self.draw.name)

    # Accept the invitation, merging queues
    def accept(self):
        q1 = self.sender.queues.get(draw=self.draw)
        q2 = self.receiver.queues.get(draw=self.draw)
        rooms1 = q1.queuetoroom_set.all()
        rooms2 = q2.queuetoroom_set.all()
        ranking = len(rooms1)
        for qtr in rooms2:
            if qtr in rooms1:
                continue
            qtr.ranking = ranking
            qtr.queue = q1
            qtr.save()
            ranking += 1
        self.receiver.queues.remove(q2)
        self.receiver.queues.add(q1)
        q2.delete()
        self.delete()

    def deny(self):
        self.delete()
        
# room review
class Review(models.Model):

    RATINGS = ( (i, i) for i in range(6) )
    
    room = models.ForeignKey('Room')
    summary = models.CharField(max_length=30)
    date = models.DateField(auto_now_add=True)
    content = models.TextField()
    rating = models.IntegerField(choices=RATINGS)
    user = models.ForeignKey('User')
    
    def __unicode__(self):
        return summary
        
class ReviewForm(ModelForm):
    class Meta:
        model = Review
        exclude = ('user', 'room')

class Photo(models.Model):

    date = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to=photopath)
    
    def __unicode__(self):
        return "Photo on %s" % (self.date)

# Information (size, timeframe, etc) about a past draw
class PastDraw(models.Model):
    draw = models.ForeignKey('Draw')
    year = models.IntegerField()
    # The number of rooms that drew in this draw
    numrooms = models.IntegerField()
    # The number of people that drew in this draw
    numpeople = models.IntegerField()

    def __unicode__(self):
        return "%s %d" % (self.draw.name, self.year)
    
# A past draw entry
class PastDrawEntry(models.Model):
    pastdraw = models.ForeignKey('PastDraw')
    room = models.ForeignKey('Room')
    # A UNIX timestamp for the time room was selected
    timestamp = models.IntegerField()
    # The number of *rooms* that drew in this draw before this room
    roomrank = models.IntegerField()
    # The number of *people* who drew in this draw before this room
    peoplerank = models.IntegerField()

    def __unicode__(self):
        return "%s %s %d" % (self.room.number, self.room.building.name,
                             self.pastdraw.year)

# A phone carrier, used for text notifications
class Carrier(models.Model):
    #email-to-text address
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name


































