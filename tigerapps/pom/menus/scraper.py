import urllib
from bs4 import BeautifulSoup


DINING_HALLS = {'WUHAL':2, 'WILCH':2, 'MADIH':1, 'FORBC':3,
                'HARGH':8, 'CENJL':5, 'GRADC':4}

url_stub = 'http://facilities.princeton.edu/dining/_Foodpro/menu.asp?locationNum=0'


class Menu:
    def __init__(self):
        self.meals = {}
    def __str__(self):
        return str(self.meals)
    __repr__ = __str__
        
class Meal:
    def __init__(self):
        self.entrees = []
    def __str__(self):
        return str(self.entrees)
    __repr__ = __str__
        
        
class Entree:
    def __init__(self, name='', vegetarian=False, vegan=False, pork=False,
                 nuts=False, earth_friendly=False):
        self.name = name
        self.vegetarian = vegetarian 
        self.vegan = vegan
        self.pork = pork
        self.nuts = nuts
        self.earth_friendly = earth_friendly
    def __str__(self):
        return str(self.__dict__)
    __repr__ = __str__
        

def scrape_single_menu(bldg_code):
    """Scrape the menu page for the given dining hall and return the data
    as a menu object"""
    hall_num = DINING_HALLS[bldg_code]
    url = url_stub + str(hall_num)
    try:
        f = urllib.urlopen(url)
    except:
        raise Exception("couldn't urlopen the menu feed url")
    
    try:
        data = f.read()
        bs = BeautifulSoup(data)
        menu = Menu()
        menu.title = bs.title.contents[0]
    
        for meal_xml in bs.find_all('meal'):
            meal = Meal()
            meal.name = meal_xml.attrs['name']
            for entree_xml in meal_xml.find_all ('entree'):
                entree = Entree()
                entree.name = entree_xml.next.contents[0]
                entree.vegan = True if entree_xml.vegan.contents[0] == 'y' else False
                entree.vegetarian = True if entree_xml.vegetarian.contents[0] == 'y' else False
                entree.pork = True if entree_xml.pork.contents[0] == 'y' else False
                entree.nuts = True if entree_xml.nuts.contents[0] == 'y' else False
                entree.earth_friendly = True if entree_xml.earth_friendly.contents[0] == 'y' else False
                meal.entrees.append(entree)
            menu.meals[meal.name] = meal
    except:
        raise Exception("couldn't parse the menu feed XML")
    finally:
        f.close()
    return menu

def scrape_all():
    """Return a list of menus, one for each dining hall"""
    menus = {}
    for hall in DINING_HALLS:
        menus[hall] = scrape_single_menu(hall)
    return menus


