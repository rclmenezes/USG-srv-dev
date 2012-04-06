from django.db import models

# Create your models here.
class Draw(models.Model):
    name = models.CharField(max_length=24)

    def __unicode__(self):
        return self.name
    
class Building(models.Model):
    name = models.CharField(max_length=30)
    pdfname = models.CharField(max_length=30)
    availname = models.CharField(max_length=30)
    draw = models.ManyToManyField(Draw)
    lat = models.FloatField()
    lon = models.FloatField()

    def __unicode__(self):
        return self.name

