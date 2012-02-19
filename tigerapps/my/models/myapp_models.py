from django.db import models
from my.admin import moviesAdmin

class USG_Movie(models.Model):
    start = DateField(help_text="When should this be posted?")
    end = DateField(help_text="When should this stop being posted?")
    imdbLink = URLField(help_text="IMDB Link (for linking, poster and rating)", blank=True, null=True)
    dates = CharField(help_text="Date(s) as how they will appear")
    poster = StdImageField(help_text="Manual overrid to imdb for poster", blank=True, null=True)
    rating = DecimalField(help_text="Manual override to imdb for rating", blank=True, null=True)
    
    class Meta:
        app_label = 'my'
        
moviesAdmin.register(UFO_Movie)