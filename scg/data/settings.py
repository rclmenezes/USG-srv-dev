import os.path as paths

# www/scg/data/settings.py -> www/scg/data -> www/scg -> www/
dir = paths.dirname(paths.dirname(paths.dirname(__file__))) + '/'
