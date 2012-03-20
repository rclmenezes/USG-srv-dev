import sys, os
sys.path.append(os.getcwd())

from parse import parse_scg_file
from settings import dir

sys.path.append(dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from apps.courses.models import Course, Offering

def main(semester, year):
    data = parse_scg_file(semester, year, 'CT')

    for row in data:
        cid = row['cid']

        authors = []
        for i in range(1,7):
            author = row['author'+str(i)]
            if author != '':
                authors.append(author)

        row.update({'authors':', '.join(authors)})
        row.update({'dep':row['dep1']})
        row.update({'num':row['num1']})
        row.update({'semester':semester})
        row.update({'year':year})

        del(row['dep1'])
        del(row['num1'])
        del(row['blank'])
        del(row['author1'])
        del(row['author2'])
        del(row['author3'])
        del(row['author4'])
        del(row['author5'])
        del(row['author6'])
        del(row['dep2'])
        del(row['num2'])
        del(row['cross_lists'])
        del(row['cid'])

        course = Course.objects.get_or_create(cid=cid)[0]
        offering = Offering.objects.get_or_create(course=course, year=year, semester=semester)

        course.__dict__.update(row)
        course.save()

if __name__ == '__main__':
    semester = sys.argv[1]
    year     = sys.argv[2]
    main(semester, year)

