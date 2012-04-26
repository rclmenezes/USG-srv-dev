import urllib
from time import strftime
import sys

class Room(object):


    def __init__(self, laundryurl):
        self._time = strftime("%Y-%m-%d %H:%M:%S")

        try:
            f = urllib.urlopen(laundryurl)
        except:
            sys.exit()

        lnid = ''
        self._washers = []
        self._dryers = []
        for line in f:
            y = []
            if 'WASHERS' in line:
                y = line.split()
                i = y.index('of')
                self._washers.append(y[i-1])
                self._washers.append(y[i+1])
            if 'DRYERS' in line:
                y = line.split()
                i = y.index('of')
                self._dryers.append(y[i-1])
                self._dryers.append(y[i+1])
                break
        
        f.close()

    def time(self):
        return self._time
    
    def washers(self):
        return self._washers

    def dryers(self):
        return self._dryers

        
