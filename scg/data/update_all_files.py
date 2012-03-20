# OK, a survival guide (written 2009/04/27 by hlian@):
# * Email Shane Smith <ds4@> if wget can't find the files you need or
#   John Grieb <jagrieb@>.
# * cid's are STRINGS, not integers. Worst primary key ever, I
#   know. But if you int() them you'll get duplicate rows in SQL. So
#   don't do that.

import commands
import os
import sys

from data import ct_parse, scg_parse, st_parse, xl_parse
from data.parse import parse_time

USAGE = """
USAGE: python update_all_files.py [--parse] semester=(F|S) year
===============================================================

Given a semester (F for fall, S for spring), and a year, downloads the
corresponding Registrar files for parsing. After downloading, you will
need to use Emacs to convert the files into UTF-8 as Python's decoder
is much less forgiving and unable to detect the file encoding. To
parse these files into the database, pass the "--parse" option.
""".strip()

def wget_files(index):
    """Given the registrar's index key, gets the four registrar text
    documents used to create the SCG database."""

    print(commands.getoutput('wget -O TF1%sCT.txt http://reg-web.princeton.edu/TF1%sCT.txt' % (index, index)))
    print(commands.getoutput('wget -O TF1%sSCG.txt http://reg-web.princeton.edu/scg_course_list_upcomeexp.txt' % index))
    print(commands.getoutput('wget -O TF1%sST.txt http://reg-web.princeton.edu/TF1%sST.txt' % (index, index)))
    print(commands.getoutput('wget -O TF1%sXL.txt http://reg-web.princeton.edu/TF1%sXL.txt' % (index, index)))

def get(sem, year):
    """Uses wget to download the registrar files. Files need to be
    converted into UTF-8 by user afterward."""

    index = parse_time(sem, year)
    print('Semester-year string: %s.' % index)
    wget_files(index)
    print('Now convert the files to UTF-8 with Unix line endings using Emacs and then pass in --parse.')

def parse(sem, year):
    """Parses the files downloaded by :func:`get`."""

    # Make sure the time is valid, but don't do anything with the
    # return values.
    parse_time(sem, year)

    ct_parse.main(sem, year)
    scg_parse.main(sem, year)
    st_parse.main(sem, year)
    xl_parse.main(sem, year)

if __name__ == '__main__':
    if '--help' in sys.argv or len(sys.argv) < 3:
        print(USAGE)
    elif '--parse' in sys.argv:
        sys.argv.remove('--parse')
        parse(sys.argv[1], sys.argv[2])
    else:
        get(sys.argv[1], sys.argv[2])
