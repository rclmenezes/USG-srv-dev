import urllib2
from bs4 import BeautifulSoup


PRINTER_BLDGS = {
    '1901': '1901H',
    '1937': '1937H',
    '1981': 'HARGH',
    'Blair': 'BLAIR',
    'Bloomberg_315': 'BLOOM',
    'Brown': 'BROWN',
    'Brush_Gallery': 'JADWH',
    # Building D
    # Butler Apts
    # Campus Club
    'CJL': 'CENJL',
    'Dod': 'DODHA',
    'Edwards': 'EDWAR',
    'Fields_Cntr': 'CFCTR',
    'Firestone': 'FIRES',
    'Fisher_213': 'FISHH',
    'Forbes': 'FORBC',
    'Forbes_Lib': 'FORBC',
    'Foulke': 'FOULK',
    'Friend_016': 'FRIEN',
    'Friend_017': 'FRIEN',
    'Frist_200': 'FRIST',
    'Frist_300': 'FRIST',
    'Grad_College': 'GRADC',
    # Hibben
    'Holder_B11': 'HOLDE',
    'Holder_B31': 'HOLDE',
    'Lauritzen_409': 'HARGH',
    # Lawrence_1
    # Lawrence_14
    'Little_North': 'LITTL',
    'Little_South': 'LITTL',
    'Madison': 'MADIS',
    'McCosh_B59': 'MCCOS',
    'New_GC': 'GRADC',
    'Pyne': 'PYNEH',
    'Scully_269': 'SCULL',
    'Scully_309': 'SCULL',
    'Spelman': 'SPELM',
    'Whitman_Lib': 'HARGH',
    'Wilcox': 'WILCH',
    'Witherspoon': 'WITHR',
    'Wright': 'PATTN',
    'Wu': 'WILCH'
}

url = 'http://campuscgi.princeton.edu/~clusters/clusterinfo.pl'

class Printer:
    def __init__(self, loc, color, status):
        self.loc = loc
        self.color = color
        self.status = str(status)
    def __str__(self):
        return self.status
    __repr__ = __str__


def scrape_single_printer(bldg_code):
    '''returns list of printers in building'''
    return scrape_all()[bldg_code]

def scrape_all():
    '''returns dict of list of printers, bldg_code:[printers]'''
    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data)
    table = bs.find('table')
    rows = table.find_all('tr')[1:]
    clusters = {}
    for row in rows:
        ps = row.find_all('p')
        loc = ps[0].contents[0][:-1].rstrip('*')
        statusTag = ps[3]
        printers = []
        for font_tag in statusTag.find_all('font'):
            try:
                status = font_tag.contents[0]
            except:
                continue
            color = font_tag.attrs['color']
            printers.append(Printer(loc.replace('_',' '), color, status))
        if loc in PRINTER_BLDGS:
            code = PRINTER_BLDGS[loc]
        else: continue

        if code in clusters:
            clusters[code] += printers
        else:
            clusters[code] = printers
            
    return clusters

