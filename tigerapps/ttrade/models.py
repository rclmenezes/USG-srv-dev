from django.db import models
from django.contrib.auth.models import User
from stdimage import StdImageField
import datetime
from decimal import Decimal

class CurrencyField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
           return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
           return None

# Method of purchase
METHOD_CHOICES = (
    (u'Au', u'Auction (Best Price Wins)'),
    (u'Fi', u'Fixed Price'),
    (u'Fr', u'Free Item/Donation'),
    (u'Mu', u'Multiple Items and Prices'),
    (u'No', u'No Price Displayed'),
    (u'Tr', u'Trade'),
)
    
'''
    Auction: just save best offer until end
    Fixed: Close immediately upon purchase
    Free: Close immediately upon claim
    Multiple: Contact seller
    No Price Displayed: Contact Seller
    Trade: Contact Seller
'''

# I think these are better hardcoded than stuck in a database where I would have 
# to reset them every time.   
CATEGORY_CHOICES = (
    (u'Ap', u'Appliances'),
    (u'Au', u'Autos'),
    (u'Ba', u'Babysitting, Baby Gear and Childcare'),
    (u'Bi', u'Bicycles'),
    (u'Bo', u'Books'),     
    (u'Cd', u'CD\'s, DVD\'s & Video Games'),
    (u'Cl', u'Clothing'),
    (u'Co', u'Computers and Electronics'),
    (u'Fu', u'Furniture'),
    (u'Ga', u'Garage Sales'), 
    (u'Gr', u'Graduation Weekend - Tickets, etc.'),
    (u'Ho', u'Housing and Apartments'),
    (u'Jo', u'Jobs (Employment Opportunities)'),
    (u'Lo', u'Lost & Found'),
    (u'Mu', u'Musical Instruments and Lessons'),
    (u'Ot', u'Other'),  
    (u'Ri', u'Rides'),
    (u'Se', u'Services'),
    (u'Sp', u'Sporting Equipment'),
    (u'Ti', u'Tickets'),
    )
  
# I figure making this a choice is only slightly less efficient than a boolean and it's A)
# easier for forms and B) easier to adapt later.  
LISTING_TYPE = (
    (u'S', u'For Sale'),
    (u'R', u'Request to Buy'),
    (u'T', u'For Rent'), # Yup, didn't think this one ahead :)
    (u'E', u'For Exchange'),
)

# Used for both requests and items for sale!
class Listing(models.Model):
    listingID = models.AutoField(primary_key=True)
    listingType = models.CharField('Listing Type', max_length=1, choices=LISTING_TYPE)
    category = models.CharField('Category', max_length=2, choices=CATEGORY_CHOICES)
    method = models.CharField('Method of Sale', max_length=2, choices=METHOD_CHOICES, blank=True, null=True) 
    title = models.CharField("Title", max_length=70)
    description = models.TextField("Description", null=True, blank=True)
    user = models.ForeignKey(User, related_name="Lister")
    picture = StdImageField('Picture (optional)', upload_to='ttrade/images/upload/', size=(560,800), blank=True)
    posted = models.DateTimeField('Date Posted')
    expire = models.DateTimeField('Date Expire')
    offers = models.ManyToManyField('Offer', null=True, blank=True)
    price = CurrencyField("Price", blank=True, null=True, decimal_places=2, max_digits=7)
    active = models.BooleanField("Is active", default=True)
    
    def __unicode__(self):
        return self.title
  
# Used for auction, fixed price and free  
class Offer(models.Model):
    offerID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="Offerer")
    price = CurrencyField("Price", blank=True, null=True, decimal_places=2, max_digits=7)
    additional = models.TextField("Message", null=True, blank=True)
    accepted = models.BooleanField("Is accepted", default=False)

    def __unicode__(self):
        return "%s: $%s" % (self.user.username, self.price)

