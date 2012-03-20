import sys, os
sys.path.append(os.getcwd())

from parse import parse_scg_file
from settings import dir
sys.path.append(dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from apps.courses.models import Course, Section, Offering

def main(semester, year):
    data = parse_scg_file(semester, year, 'ST')
    for row in data:
        cid = row['cid']
        sid = row['sid']

        days ='-'.join([row['day1'],row['day2'],row['day3'],row['day4'],row['day5']])
        row['days'] = days

        import datetime, time
        from datetime import datetime
        format = '%I:%M %p'
        if row['begins'] != 'TBA' and row['begins'] != '':
            length = datetime(*(time.strptime(row['ends'], format)[0:6])) - datetime(*(time.strptime(row['begins'], format)[0:6]))
            length = int(length.seconds / 60)
        else:
            length = 0
        row['length'] = length

        del(row['dep'])
        del(row['num'])
        del(row['term'])
        del(row['blank'])
        del(row['sid'])
        del(row['cid'])

        try:
            course = Course.objects.get(pk=cid)

            offering = Offering.objects.get_or_create(course=course, year=year, semester=semester)[0]

            row.update({'offering':offering})

            s, created = Section.objects.get_or_create(sid=sid,defaults=row)
            if not created:
                s.__dict__.update(row)
                s.save()

        except Exception, e:
            print 'course %s does not exist' % cid
            print e

if __name__ == '__main__':
    semester = sys.argv[1]
    year     = sys.argv[2]
    main(semester, year)
