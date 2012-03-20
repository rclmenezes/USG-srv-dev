import sys, os
sys.path.append(os.getcwd())

from parse import parse_scg_file
from settings import dir
sys.path.append(dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from apps.courses.models import Course, Offering
from apps.professors.models import Professor

def get_first_name(name):
    name = name.split(' ')
    del(name[-1])

    if len(name) == 0:
        return ""

    return name[0]

def get_last_name(name):
    return name.split(' ')[-1]

def get_middle_name(name):
    name = name.split(' ')
    del(name[0])

    if len(name) == 0:
        return ""

    del(name[-1])
    return ' '.join(name)


def professor_data(row, num):
    id = 'professor' + str(num)
    pid = 'pid' + str(num)
    return {'first_name':   get_first_name(row[id]),
            'last_name':    get_last_name(row[id]),
            'middle_names': get_middle_name(row[id]),
            'picture_url':  'https://websurvey.princeton.edu/FaceBook/Default/%s.jpg' % row[pid],
            }

def main(semester, year):
    data = parse_scg_file(semester, year, 'SCG')
    P = Professor.objects

    for row in data:
        # Add *or update* professors given the new information.
        for i in (1, 2, 3):
            pid = 'pid' + str(i)
            if not row[pid]: continue

            data = professor_data(row, i)
            p, created = P.get_or_create(pid=row[pid], defaults=data)
            if not created:
                p.__dict__.update(data)
                p.save()

        course_dict = {'dep': row['dep1'],
                       'num': row['num1'],
                       'dr': row['dr'],
                       'cross_list': row['dep2'] + u' ' + row['num2'],
                       'title': row['title'],
                       'is_cancelled': row['is_cancelled'],
                       'is_closed': row['is_closed'],
                       }

        course = Course.objects.get_or_create(cid=row['cid'],
                                              defaults=course_dict)[0]

        for i in (1, 2, 3):
            pid = 'pid' + str(i)
            if row[pid] != '':
                p = P.get(pid=row[pid])
                offering = Offering.objects.get_or_create(course=course,
                                                          year=year,
                                                          semester=semester)[0]
                offering.professors.add(p)

if __name__ == '__main__':
    semester = sys.argv[1]
    year = sys.argv[2]
    main(semester, year)

