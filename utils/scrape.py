#general scraping utility using curl, to avoid apache gayness

import subprocess as sub

def log(s):
    pass
    #f = open('/srv/tigerapps/slog', 'a')
    #f.write(s + '\n')
    #f.close()

def scrapePage(url):
    '''Return a unicode string of data at the specified url'''
    log('scraping ' + url)
    data = unicode(sub.check_output(["curl", url]), 'utf-8')
    log('done scraping')
    return data
