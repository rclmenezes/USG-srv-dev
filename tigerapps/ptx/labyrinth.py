import re
import urllib

PRICE = re.compile(r'Princeton --&#62; New for \$(\d+\.\d+)')
URL = 'http://www.labyrinthbooks.com/all_detail.aspx?isbn=%s'

def labyrinthprice(isbn13):
    '''Scrapes price from labyrinth.'''

    page = urllib.urlopen(URL % isbn13).read()
    match = PRICE.search(page)

    if match:
        return match.group(1)
    else:
        return "0.00"
