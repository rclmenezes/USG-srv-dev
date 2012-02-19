import re

def getnavbar(request):
    home = {'navbar1': "selected", 'navbar2': "deselected",
            'navbar3': "deselected", 'navbar4': "deselected", 
            'navbar5': "deselected"}
    browse = {'navbar1': "deselected", 'navbar2': "selected",
            'navbar3': "deselected", 'navbar4': "deselected",
    		'navbar5': "deselected"}
    offer = {'navbar1': "deselected", 'navbar2': "deselected",
            'navbar3': "selected", 'navbar4': "deselected",
            'navbar5': "deselected"}
    wishlist = {'navbar1': "deselected", 'navbar2': "deselected",
            'navbar3': "deselected", 'navbar4': "selected",
            'navbar5': "deselected"}
    help = {'navbar1': "deselected", 'navbar2': "deselected",
            'navbar3': "deselected", 'navbar4': "deselected",
            'navbar5': "selected"}
    none = {'navbar1': "deselected", 'navbar2': "deselected",
            'navbar3': "deselected", 'navbar4': "deselected",
            'navbar5': "deselected"}

    fullurl = request.build_absolute_uri()
    match = re.search(r'(browse)|(search)|(buy)', fullurl)
    if match:
        return browse

    match = re.search(r'offer', fullurl)
    if match:
        return offer

    match = re.search(r'(request)|(wishlist)', fullurl)
    if match:
        return wishlist

    match = re.search(r'help', fullurl)
    if match:
        return help

    match = re.search(r'account', fullurl)
    if match:
        return none

    return home


