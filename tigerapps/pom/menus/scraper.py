from utils.scrape import scrapePage
import urllib3, urllib2
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
    def __init__():
        self.attributes = {}

    def __str__(self):
        return str(self.__dict__)
    __repr__ = __str__
        

def scrape_single_menu(bldg_code):
    """Scrape the menu page for the given dining hall and return the data
    as a menu object"""
    hall_num = DINING_HALLS[bldg_code]
    url = url_stub + str(hall_num)
    
    content = scrapePage(url)
    bs = BeautifulSoup(content)
    menu = Menu()
    menu.title = bs.title.contents[0]

    for meal_xml in bs.find_all('meal'):
        meal = Meal()
        meal.name = meal_xml.attrs['name']
        for entree_xml in meal_xml.find_all('entree'):
            entree = Entree()
            entree['name'] = entree_xml.next.contents[0]
            for c in entree_xml.contents[1:]:
                entree[c.name] = c.contents[0]
            meal.entrees.append(entree)
        menu.meals[meal.name] = meal

    log('exiting from scrape_single_menu')
    return menu

def scrape_all():
    """Return a list of menus, one for each dining hall"""
    menus = {}
    for hall in DINING_HALLS:
        menus[hall] = scrape_single_menu(hall)
    return menus


