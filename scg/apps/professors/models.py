from django.db import models

# Create your models here.
class Professor(models.Model):
    pid = models.CharField(max_length=30, primary_key=True)

    last_name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    middle_names = models.CharField(max_length=255, blank=True)

    gpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    num_reviews = models.IntegerField(default=0)


    picture_url = models.TextField(blank=True)

    def __unicode__(self):
        return u' '.join((self.first_name,
                          self.middle_names,
                          self.last_name,))

    class Meta:
        ordering = ['last_name','first_name','middle_names']

    class Admin:
        pass
