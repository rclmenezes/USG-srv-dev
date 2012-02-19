import base64
import hashlib
import hmac
import os
import time
import urllib

from BeautifulSoup import BeautifulSoup, NavigableString
from collections import defaultdict

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings

from ptx.models import Offer, Book, Course, User
from ptx.labyrinth import labyrinthprice

ACCESS_KEY = 'AKIAI3TICBLED3J2YH6A'
SECRET_KEY = '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'

# Fill in the ISBN in keys "ItemId" and "Keywords".
BY_ISBN = dict(Service='AWSECommerceService',
               Operation='ItemLookup',
               IdType='ISBN',
               Version='2009-03-31',
               SearchIndex='Books',
               ResponseGroup='ItemAttributes,Images,EditorialReview')

# Fill in the ISBN in the key "Keywords".
TO_ASIN = dict(Service='AWSECommerceService',
               Operation='ItemSearch',
               Version='2009-03-31',
               SearchIndex='Books',
               ResponseGroup='Small')

def cleanisbn(isbn):
    '''returns a string of length 10 or 13 that contains only numbers (or X)
       using isbn as input. if this is not possible, returns an
       empty string. note that check digits are not checked because
       publishers may calculate them incorrectly!'''

    cleaned = filter(lambda x: x.isdigit() or x.upper() == 'X', isbn)

    if len(cleaned) == 10 or len(cleaned) == 13:
       return cleaned
    else:
       return ''

def aws_url(query, additional=dict()):
    '''Takes a dictionary of request data and signs it for an Amazon
    request. Takes an additional dictionary to update the query. Does
    not mutate either dictionary. Returns the response body.'''

    # See <http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html?Query_QueryAuth.html>
    query = dict(query)
    query.update(additional)
    query['AWSAccessKeyId'] = ACCESS_KEY
    format = '%Y-%m-%dT%H:%M:%SZ'
    query['Timestamp'] = time.strftime(format, time.gmtime())

    # Query key, value pairs must be sorted alphabetically.
    items = query.items()
    items = [(x.encode('utf8'), y.encode('utf8')) for x, y in items]
    items.sort()
    # Amazon does not want quote_plus. Poor quote_plus.
    old_quote_plus = urllib.quote_plus
    try:
        urllib.quote_plus = urllib.quote
        query = urllib.urlencode(items)
    finally:
        urllib.quote_plus = old_quote_plus

    # Specific order mentioned in the Amazon docs: verb, lowercase
    # host header, '/onca/xml', query string.
    req  = '\n'.join(['GET', 'ecs.amazonaws.com', '/onca/xml', query])
    # Specific hash mentioned in Amazon docs: SHA-256.
    hm = hmac.new(SECRET_KEY, req, hashlib.sha256)
    sign = urllib.quote(base64.b64encode(hm.digest()))
    url = 'http://ecs.amazonaws.com/onca/xml?%s&Signature=%s' % (query, sign)
    return url

def book_details(isbn):
    '''Looks up an ISBN on Amazon. Returns :obj:`None` if no book is
    found. Otherwise returns a :class:`Book` model instance. Model
    fields that could not be filled out will be empty. Requires
    network access to Amazon and Labryinth.'''

    isbn = cleanisbn(isbn)
    url = aws_url(BY_ISBN, dict(ItemId=isbn, Keywords=isbn))
    # TODO: Catch possible URL open error
    data = urllib.urlopen(url).read().decode('utf8')

    # Note: BeautifulSoup lowercases everything, tags and attributes
    # and all.
    doc = BeautifulSoup(data)

    # Return None on no results
    item = doc.items.item
    if not len(doc.items.item):
        return None

    ia = item.itemattributes
    r = defaultdict(unicode)
    for key in 'title author edition publisher'.split():
        if getattr(ia, key):
            r[key] = getattr(ia, key).string

    if ia.isbn:
        r['isbn10'] = ia.isbn.string
    if ia.ean:
        r['isbn13'] = ia.ean.string
    if ia.publicationdate:
        r['year'] = int(ia.publicationdate.string[0:4])
    if ia.listprice:
        price = float(ia.listprice.amount.string) / 100.0
        r['list_price'] = u"%.2f" % price
    if item.editorialreviews and item.editorialreviews.editorialreview:
        r['desc'] = item.editorialreviews.editorialreview.content.string
    if item.detailpageurl:
        r['amazon_info'] = item.detailpageurl.string

    if item.mediumimage:
        img_name = r['isbn13'] + ".jpg"
        r['img_name'] = img_name
        r['img'] = os.path.join(settings.BOOK_CACHE_DIR, img_name)
        r['img_http'] = "/book_cache/" + img_name
        r['amazon_img'] = item.mediumimage.url.string

        if os.path.exists(r['img']):
            os.remove(r['img'])

        urllib.urlretrieve(r['amazon_img'], r['img'])
    else:
        r['img_name'] = 'default_book.jpg'
        r['img'] = os.path.join(settings.STATIC_DOC_ROOT, r['img_name'])
        r['img_http'] = '/css/img/' + r['img_name']
        r['amazon_img'] = ''

    r['labyrinth_price'] = labyrinthprice(r['isbn13'])

    # BeautifulSoup.NavigableString is not fully unicode!
    # http://stackoverflow.com/questions/1102465/
    for key in r:
        if isinstance(r[key], NavigableString):
            r[key] = unicode(r[key])

    return Book(
            isbn13          = r['isbn13'],
            isbn10          = r['isbn10'],
            title           = r['title'],
            desc            = r['desc'] or None,
            author          = r['author'],
            edition         = r['edition'] or None,
            year            = r['year'],
            publisher       = r['publisher'],
            list_price      = r['list_price'] or None,
            amazon_img      = r['amazon_img'],
            amazon_info     = r['amazon_info'],
            labyrinth_price = r['labyrinth_price'],
            imagename       = r['img_http'])

def isbn_to_asin(isbn):
    '''Implements Amazon's ItemSearch.'''

    url = aws_url(TO_ASIN, dict(Keywords=isbn))
    data = urllib.urlopen(url).read().decode('utf8')
    doc = BeautifulSoup(data)

    # TODO: ERROR PROCESSING
    asin = doc.itemsearchresponse.items.item.asin.string
    return unicode(asin)

