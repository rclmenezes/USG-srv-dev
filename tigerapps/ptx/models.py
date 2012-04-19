from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
import re
from ptx import labyrinth
from ptx.dept import get_dept_name, get_dept

class Course(models.Model):
    dept    = models.CharField(max_length=5)
    num     = models.IntegerField()

    def depthasbooks(self):
        county = Book.objects.filter(course__dept=self.dept).count()
        return county > 0

    # good example of better django code
    def hasbooks(self):
        return self.book_set.all().count() > 0

    def hasunofferedbooks(self):
        for book in self.book_set.all():
            if book.hasOfferings():
                return False
        return True

    def hasofferings(self):
        numstr = unicode(self.num)
        county = Q(book__course__dept=self.dept) \
            & Q(book__course__num=numstr) \
            & Q(status='o')
        county = Offer.objects.filter(county).count()
        return county > 0

    def numofferings(self):
        numstr = unicode(self.num)
        county = Offer.objects.filter(Q(book__course__dept=self.dept) &
                                      Q(book__course__num=numstr) &
                                      Q(status='o')).count()
        return unicode(county)

    def multipleOfferings(self):
        return self.num > 1

    def hasrequests(self):
        numstr = unicode(self.num)
        county = Request.objects.filter(Q(book__course__dept=self.dept) &
                                        Q(book__course__num=numstr)).count()
        return county > 0

    def numrequests(self):
        numstr = unicode(self.num)
        county = Request.objects.filter(Q(book__course__dept=self.dept) &
                                        Q(book__course__num=numstr)).count()
        return unicode(county)

    def deptname(self):
        return get_dept_name(self.dept)

    def deptcontact(self):
        return get_dept(self.dept)

    class Meta:
        unique_together = ('dept', 'num')

    def __unicode__(self):
        if self.num:
            return u"%s %s" % (self.dept, self.num)
        else:
            # For special tags, like #misc.
            return u"%s" % self.dept

    def __repr__(self):
        return "<Course(%s %s)>" % (self.dept, self.num)

class Book(models.Model):
    isbn13      = models.CharField(max_length=13, primary_key=True)
    isbn10      = models.CharField(max_length=10, unique=True)
    title       = models.CharField(max_length=512)
    desc        = models.TextField(null=True)
    author      = models.CharField(max_length=512)
    edition     = models.CharField(max_length=512, null=True)
    year        = models.IntegerField()
    publisher   = models.CharField(max_length=256)
    list_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    imagename   = models.CharField(max_length=512)
    course      = models.ManyToManyField(Course)

    # Links
    amazon_info  = models.CharField(max_length=1024)
    amazon_img   = models.CharField(max_length=1024) # Url to amazon thumbnail

    # Prices from other sites
    labyrinth_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Class constants.
    re_associate = re.compile(ur'%26tag%3Dws')

    @property
    def associate_link(self):
        return Book.re_associate.sub(u'&tag=princtextbexc-20',
                                     self.amazon_info)

    def hasRequests(self):
        return self.numOfferings() > 0

    def numRequests(self):
        return Request.objects.filter(book__isbn13=self.isbn13).count()

    def hasOfferings(self):
        return self.numOfferings() > 0

    def numOfferings(self):
        return self.offer_set.filter(status='o').count()

    def bestprice(self):
        """Returns the best price offered on this book in units of
        dollars."""

        offers = self.offer_set.filter(status='o').order_by('price')
        if len(offers) > 0:
            return unicode(offers[0].price)
        else:
            # shouldn't be calling this function if no offers
            return u"No offers available"

    def __repr__(self):
        return '<Book(%s)>' % unicode(self.title)

class User(models.Model):
    net_id          = models.CharField(max_length=10, primary_key=True)
    first_name      = models.CharField(max_length=256)
    last_name       = models.CharField(max_length=256)
    dorm_name       = models.CharField(max_length=50)
    dorm_room       = models.CharField(max_length=50)

    ratings_up      = models.IntegerField(default=0)
    ratings_down    = models.IntegerField(default=0)

    dollars_spent   = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    dollars_earned  = models.DecimalField(max_digits=10, decimal_places=2, default='0')

    def thumbs_up(self):
        self.ratings_up = self.ratings_up + 1
        self.save()

    def thumbs_down(self):
        self.ratings_down = self.ratings_down + 1
        self.save()

    # return string of user rating percentage
    def getRating(self):
        total_ratings = self.ratings_up + self.ratings_down
        # don't divide by 0
        if total_ratings > 0:
            percentage = float(self.ratings_up) / float(total_ratings)
            return '%2.0f%% (%d/%d)' % (percentage * 100, self.ratings_up, total_ratings)

        else:
            return mark_safe('New User')

    # we can put save some user settings here, add more about their profile,
    # etc.
    def __repr__(self):
        return '<User(%s)>' % self.net_id

STATUS_CHOICES = (
    ('o', 'Open'),      # User is selling/willing to lend book
    ('p', 'Pending'),   # User is engaged in a transaction
    ('c', 'Closed'),    # User has completed transaction
)

CONDITION_CHOICES = (
    ('a', 'New'),
    ('b', 'Like New'),
    ('c', 'Very Good'),
    ('d', 'Good'),
    ('e', 'Acceptable'),
)

TYPE_CHOICES = (
    ('s', 'Selling'),
    ('l', 'Lending'),
)

SEMESTER_CHOICES = (
    ('f', 'Fall'),
    ('s', 'Spring'),
)

class Offer(models.Model):
    book    = models.ForeignKey(Book)
    user    = models.ForeignKey(User)

    # Transaction Info
    status      = models.CharField(max_length=1, choices=STATUS_CHOICES)
    type        = models.CharField(max_length=1, choices=TYPE_CHOICES)
    allow_bids  = models.BooleanField()
    has_rated = models.BooleanField(default=False) # has the SELLER rated the BUYER yet?

    # Product Info
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    condition   = models.CharField(max_length=1, choices=CONDITION_CHOICES)
    desc        = models.TextField()

    # Date used info
    semester    = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    year        = models.IntegerField()

    date_open = models.DateField(auto_now_add=True)
    date_pending = models.DateField(null=True)
    date_closed= models.DateField(null=True)

    def rate_seller(self, rating, netid_check):
        if self.request_set.all().count() > 0:
            req = self.request_set.all()[0]
            if req.user.net_id == netid_check and not req.has_rated:
                if rating > 0:
                    self.user.thumbs_up()
                else:
                    self.user.thumbs_down()

                req.has_rated = True
                req.save()

    def rate_buyer(self, rating, netid_check):
        if self.request_set.all().count() > 0:
            req = self.request_set.all()[0]
            if self.user.net_id == netid_check and not self.has_rated:
                if rating > 0:
                    req.user.thumbs_up()
                else:
                    req.user.thumbs_down()

                self.has_rated = True
                self.save()


    def buyerid(self):
        if self.request_set.all().count() > 0:
            return self.request_set.all()[0].user.net_id
        else:
            return "no buyer"

    def is_pending(self):
        if self.status == 'p':
            return True
        if not self.hasClosedRequest():
            return True
        if not self.has_rated:
            return True
        if self.hasPendingRequest():
            return True
        return False

    def hasClosedRequest(self):
        return self.request_set.filter(status='c').count() > 0

    def hasPendingRequest(self):
        if self.request_set.filter(status='p').count() > 0:
            return True
        if self.request_set.filter(has_rated=False).count() > 0:
            return True
        return False

    def getCondition(self):
        for i in range(len(CONDITION_CHOICES)):
            if (self.condition == CONDITION_CHOICES[i][0]):
                return CONDITION_CHOICES[i][1]
        return ""

    def firstchoice(self):
        return self.book.course.all()[0]

    def __repr__(self):
        return "<Offer(user=%s, book=%s)>" % (repr(self.user), repr(self.book))

class Request(models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    status = models.CharField(max_length='1', choices=STATUS_CHOICES, default='o')
    maxprice = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')

    date_open = models.DateField(auto_now_add=True)
    date_pending = models.DateField(null=True)
    date_closed = models.DateField(null=True)

    offer = models.ForeignKey(Offer, null=True)

    has_rated = models.BooleanField(default=False) # has the BUYER rated the SELLER yet?

    def __repr__(self):
        return "<Request(%s: %s)>" % (repr(self.user), repr(self.book))

