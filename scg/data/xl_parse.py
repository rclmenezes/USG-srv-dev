import sys
import os
sys.path.append(os.getcwd())

from settings import dir
from parse import parse_scg_file

sys.path.append(dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from apps.courses.models import Course, CrossList
from apps.professors.models import Professor

def main(semester, year):
    data = parse_scg_file(semester, year, 'XL')
    for row in data:
        cid = row['cid']
        try:
            course = Course.objects.get(pk=cid)
        except:
            print "Weird, no object found with key " + cid

        course.dep = row['dep']
        course.num = row['num']
        #course.save()

        crosslists = row['cross_list']
        crosslists = map(lambda x: x.split(' '), crosslists.split('/'))
        for (dep, num) in crosslists:
            cl = CrossList.objects.get_or_create(course=course,dep=dep,num=num)

if __name__ == '__main__':
    semester = sys.argv[1]
    year     = sys.argv[2]
    main(semester, year)
