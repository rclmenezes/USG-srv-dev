from django.db import models
from stdimage import StdImageField

class USG_Movie(models.Model):
    start = models.DateField(help_text="When should this be posted?")
    end = models.DateField(help_text="When should this stop being posted?")
    dates = models.CharField(max_length=30, help_text="Date(s) as how they will appear")
    title = models.CharField(max_length=40, help_text="Title of movie")
    poster = StdImageField(help_text="Poster", upload_to="myapps/movies/Images")
    rating = models.CharField(help_text="Rating of movie", max_length="40")