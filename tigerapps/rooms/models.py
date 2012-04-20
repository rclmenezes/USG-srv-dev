from django.db import models

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
