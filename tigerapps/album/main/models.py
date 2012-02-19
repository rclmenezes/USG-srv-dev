"""Django models for TigerAlbum. Contains types for photos, comments, as well
as functions for operating on those types."""

from datetime import datetime
from hashlib import sha1 as prf
from math import pi, log, sin
from PIL import Image
from StringIO import StringIO

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
#from django.db.models import Count

# Tolerance for overlap--how many pixels of overlap is allowed
OVERLAP_TOLERANCE = 0

# Constants for the earth's geometry used for pixel-distance conversions
OFFSET = 268435456
RADIUS = OFFSET / pi

class Photo(models.Model):
    """Model representing a photo.

    Fields:
    caption -- the caption for the photo
    location_x -- longitude coordinate of the photo's position
    location_y -- latitude coordinate of the photo's position
    photo -- the image
    height -- height of the image in pixels
    width -- width of the image in pixels
    approved -- was the photo approved?
    dt_submitted -- submission date
    n_flagged -- number of flags for inappropriate content
    n_likes -- number of facebook likes
    ip -- ip address from which the photo was submitted
    """

    caption = models.TextField()
    location_x = models.FloatField('x GPS coordinate', null=True)
    location_y = models.FloatField('y GPS coordinate', null=True)
    photo = models.ImageField(upload_to='photos', height_field='height',
                              width_field='width')
    thumbnail = models.ImageField(upload_to='photos')
    height = models.FloatField()
    width = models.FloatField()
    approved = models.BooleanField()
    dt_submitted = models.DateTimeField('date submitted')
    n_flagged = models.IntegerField('number of times flagged')
    n_flagged_offs = models.IntegerField('number of times flagged for offensive content')
    n_flagged_cprv = models.IntegerField('number of times flagged for copyright violation')
    n_flagged_othr = models.IntegerField('number of times flagged for other reason')
    n_likes = models.IntegerField('number of times liked')
    ip = models.IPAddressField()
    permalink = models.CharField(max_length=10)

    @property
    def popularity(self):
        """Implement Hacker News' popularity algorithm, which I've
        always liked: $p / (t + 2) ** 1.5$ where p is how many
        comments/likes and t is the time delta."""

        # Weight likes more than comments.
        # plus the number of likes times 1
        pop_factor = len(self.comments.all()) * 2
        time_factor = datetime.now() - self.dt_submitted
        time_factor = time_factor.days * 24 + time_factor.seconds / 3600.0
        return pop_factor / (time_factor + 2) ** 1.5

    @classmethod
    def get_by_permalink(klass, permalink):
        photos = list(klass.objects.filter(permalink__exact=permalink))
        if not photos:
            return None
        return photos[0]

    def age(self):
        """Gives the age of the photo."""
        time_diff = datetime.now() - self.dt_submitted
        time_diff = time_diff.days * 24 + time_diff.seconds / 3600.0
        return time_diff


    def pixel_dist(self, other, zoom):
        """Returns a tuple containing the x,y pixel distance between this photo
        and another at the specified zoom level"""

        def long_to_x(location_x):
            """Converts a given longitude to a pixel coordinate"""
            return int(round(OFFSET+RADIUS*location_x*pi/180, 0))

        def lat_to_y(location_y):
            """Converts a given latitude to a pixel coordinate"""
            return int(round(OFFSET-RADIUS*log((1+sin(location_y*pi/180))/
                                               (1-sin(location_y*pi/180)))/2))

        x_dist = abs((long_to_x(self.location_x) - long_to_x(other.location_x))
                     >> (21 - zoom))
        y_dist = abs((lat_to_y(self.location_y) - lat_to_y(other.location_y))
                     >> (21 - zoom))

        return x_dist, y_dist

    def overlaps(self, other, zoom):
        """Checks whether this photo overlaps another specified photo other"""
        x_dist, y_dist = self.pixel_dist(other, zoom)

        if ((x_dist < (128 - OVERLAP_TOLERANCE)) and 
            (y_dist < (128 - OVERLAP_TOLERANCE))):
            return True

        return False


    def save_with(self, filelike):
        """Saves the model instance with a filelike object
        representing photograph."""

        checksum = prf()
        while True:
            blob = filelike.read(1024)
            if not blob:
                break
            checksum.update(blob)
        filelike.seek(0)


        thumb = Image.open(filelike)
        width, height = thumb.size
        if width > height:
            size = 128, height/(width/128)
        else:
            size = width/(height/128), 128

        thumb.thumbnail(size, Image.ANTIALIAS)

        # Create a file-like object to write thumb data (thumb data previously
        # created using PIL, and stored in variable 'thumb')
        thumb_io = StringIO()
        thumb.save(thumb_io, format='JPEG')

        # Create a new Django file-like object to be used in models as
        # ImageField using InMemoryUploadedFile.  If you look at the source in
        # Django, a SimpleUploadedFile is essentially instantiated similarly
        # to what is shown here
        thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg',
                                          'image/jpeg', thumb_io.len, None)

        self.thumbnail.save(checksum.hexdigest() + '_t.jpg', File(thumb_file),
                            save=False)
        self.photo.save(checksum.hexdigest() + '.jpg', File(filelike),
                        save=True)

    @classmethod
    def popular(cls, xmin, xmax, ymin, ymax, num):
        """Returns the num most popular photos within the coordinate bounds."""
        qset = cls.objects
        qset = qset.filter(location_x__gte=xmin,
                           location_x__lte=xmax,
                           location_y__gte=ymin,
                           location_y__lte=ymax,
                           approved=True)
        qset = sorted(qset, key=lambda photo: photo.popularity,
                      reverse=True)[:num]
        return list(qset)

    @classmethod
    def newest(cls, xmin, xmax, ymin, ymax, num):
        """Returns the num newest photos within the coordinate bounds."""
        qset = cls.objects
        qset = qset.filter(location_x__gte=xmin,
                           location_x__lte=xmax,
                           location_y__gte=ymin,
                           location_y__lte=ymax,
                           approved=True)
        qset = sorted(qset, key=lambda photo: photo.age,
                      reverse=False)[:num]
        return list(qset)

    @classmethod
    def popular_by_age(cls, xmin, xmax, ymin, ymax, num, threshold):
        """Returns the num most popular photos within the coordinate bounds
        that were more recently submitted than the threshold."""
        qset = cls.objects
        qlist = []
        qset = qset.filter(location_x__gte=xmin,
                           location_x__lte=xmax,
                           location_y__gte=ymin,
                           location_y__lte=ymax,
                           approved=True)
        qset = sorted(qset, key=lambda photo: photo.popularity,
                      reverse=True)[:num]
        for item in qset:
            if item.age() < threshold:
                qlist.append(item)
        return qlist[:num]

    @classmethod
    def search(cls, query):
        """Performs a search for the query term within captions and
        comments."""
        captioned = cls.objects.filter(caption__icontains=query, approved=True)
        commented = cls.objects.filter(comments__comment__icontains=query,
                                         approved=True)
        return set(captioned) | set(commented)

    def save(self, *a, **kw):
        """Attach a non-monotonic permalink to each photo,
        post-save."""

        super(Photo, self).save(*a, **kw)
        h = prf()
        h.update(str(self.id))
        h.update(str(self.photo.name))
        self.permalink = h.hexdigest()[0:8]
        super(Photo, self).save()

class Comment(models.Model):
    """Model representing a comment.

    Fields:
    photo -- the photo the comment is associated with
    parent -- the photo's parent comment
    comment -- the comment text
    author -- the comment's author
    dt_posted -- date when the comment was posted
    n_flagged -- number of flags for inappropriate content
    ip -- ip address the comment was submitted from
    """

    photo = models.ForeignKey(Photo, related_name='comments')
    parent = models.ForeignKey('Comment', related_name='children', null=True,
                               blank=True)
    comment = models.TextField()
    author = models.TextField()
    dt_posted = models.DateTimeField('date posted')
    n_flagged = models.IntegerField('number of times flagged')
    ip = models.IPAddressField()

    @classmethod
    def posts(cls, photoid):
        """Returns all comments associated with a given photoid"""
        return cls.objects.filter(photo=photoid, parent=None)
