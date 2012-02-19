from django.db import models

class DVD(models.Model):
    dvd_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sortname = models.CharField(max_length=100)
    amountTotal = models.IntegerField('Amount Overall')
    amountLeft = models.IntegerField('Amount left in the office')
    imdbID = models.CharField(max_length=20, null=True, blank=True)
    timesRented = models.IntegerField('Times Rented')
    
    def __unicode__(self):
        return self.name
        
class Rental(models.Model):
    rentalID = models.AutoField(primary_key=True)   
    netid = models.CharField(max_length=8)
    dvd = models.ForeignKey('DVD')
    dateRented = models.DateTimeField('date rented', blank=True)
    dateDue = models.DateTimeField('date due', blank=True)
    dateReturned = models.DateTimeField('date returned', blank=True, null=True)

    def __unicode__(self):
        return self.dvd.name
        
class RentalCopy(models.Model):
    rental = models.ForeignKey('Rental')
    copy = models.IntegerField('Copy Number')
        
class Notice(models.Model):
    netid = models.CharField(max_length=8)
    dvd = models.ForeignKey('DVD')
    
    def __unicode__(self):
        return self.netid + " " + self.dvd.name