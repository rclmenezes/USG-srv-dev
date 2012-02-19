import os
import time
from wsgiref.handlers import format_date_time

def thisdirpath(p, current_filename):
    thisdir = os.path.dirname(current_filename)
    return os.path.abspath(os.path.join(thisdir, p))

def datetime_to_json(dt):
    return format_date_time(time.mktime(dt.timetuple()))
