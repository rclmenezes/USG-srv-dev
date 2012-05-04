import re
import urllib2
from lxml import etree
from lxml.cssselect import CSSSelector
import datetime

from django.db import models
from django.template.loader import render_to_string
from apps.professors.models import Professor
from data.parse import parse_time


def get_this_term():
    today = datetime.date.today()
    if today.month <= 1 or today.month >= 7:
        return ('F', str(today.year), 'S', str(today.year+1))
    else:
        return ('S', str(today.year), 'F', str(today.year))

THIS_SEMESTER, THIS_YEAR, NEXT_SEMESTER, NEXT_YEAR = get_this_term()
TERM = '1' + parse_time(THIS_SEMESTER, THIS_YEAR)
CSS_TIMETABLE = CSSSelector('#timetable')
CSS_TIMETABLE_SUPERFLUOUS = CSSSelector('div[align="right"]')


class Course(models.Model):
    cid = models.CharField(max_length=20, blank=True, primary_key=True)

    dep = models.CharField(max_length=10, blank=True)
    num = models.CharField(max_length=30, blank=True)

    gpa = models.DecimalField(max_digits=5, default=0, decimal_places=2, null=True, blank=True)
    num_reviews = models.IntegerField(default=0)

    year = models.CharField(max_length=10, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    dr = models.CharField(max_length=10, blank=True)

    authors = models.CharField(max_length=512, blank=True)

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    registrar_info = models.TextField(blank=True, null=True)

    grade_midterm = models.CharField(max_length=10, blank=True)
    grade_paper_for_midterm = models.CharField(max_length=10, blank=True)
    grade_final = models.CharField(max_length=10, blank=True)
    grade_paper_for_final = models.CharField(max_length=10, blank=True)
    grade_other_exam = models.CharField(max_length=10, blank=True)
    grade_take_home_midterm = models.CharField(max_length=10, blank=True)
    grade_design_projects = models.CharField(max_length=10, blank=True)
    grade_take_home_final = models.CharField(max_length=10, blank=True)
    grade_programming = models.CharField(max_length=10, blank=True)
    grade_quizzes = models.CharField(max_length=10, blank=True)
    grade_lab_reports = models.CharField(max_length=10, blank=True)
    grade_papers = models.CharField(max_length=10, blank=True)
    grade_oral_presentation = models.CharField(max_length=10, blank=True)
    grade_term_paper = models.CharField(max_length=10, blank=True)
    grade_precept = models.CharField(max_length=10, blank=True)
    grade_problem_sets = models.CharField(max_length=10, blank=True)
    grade_other = models.CharField(max_length=10, blank=True)

    pdf_option = models.CharField(max_length=10, blank=True)
    pdf_only = models.CharField(max_length=10, blank=True)
    max_enrollment = models.CharField(max_length=10, blank=True)
    audit_option = models.CharField(max_length=10, blank=True)
    app_or_interview_required = models.CharField(max_length=10, blank=True)
    pre_course_preference_required = models.CharField(max_length=10, blank=True)
    freshmen_allowed = models.CharField(max_length=10, blank=True)
    upperclassmen_only = models.CharField(max_length=10, blank=True)
    requirement_group = models.CharField(max_length=10, blank=True)
    required_for_concentrators = models.CharField(max_length=10, blank=True)
    course_card_initialed_by = models.CharField(max_length=10, blank=True)

    is_cancelled = models.CharField(max_length=10, blank=True)
    is_closed = models.CharField(max_length=10, blank=True)

    other_info = models.TextField(blank=True)

    professors = models.ManyToManyField(Professor, null=True, blank=True)

    cross_list = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.dep + ' ' + self.num + ': ' + self.title

    def __unicode__(self):
        return self.dep + u' ' + self.num + u': ' + self.title

    @property
    def offered(self):
        return self.year == NEXT_YEAR and self.semester == NEXT_SEMESTER

    def quick_summary(self):
        t = 'courses/dept_quick_summary.html'
        data = {
            'd': self,
            'high_grade': float(self.gpa) >= 3.50,
            'offered': self.offered,
            }

        return render_to_string(t, data)

    def high_grade(self):
        return float(self.gpa) >= 3.50

    def update_official_info(self):
        """Retrieves the correct value for :obj:`self.registrar_info`
        from the Registrar since this information is not available to
        us during from the Registrar's parsing files."""

        # This is an ugly brittle procedure, so follow closely. First,
        # parse the course details page into a lxml tree.
        url = 'http://registrar.princeton.edu/course-offerings/course_details.xml?courseid=%s&term=%s' % (self.cid, TERM)
        body = urllib2.urlopen(url).read()
        t = etree.fromstring(body, etree.HTMLParser())
        timetable = CSS_TIMETABLE(t)[0]

        # Take out all nodes that are siblings to the <h2> title and
        # come before it. They're junk nodes that we don't want.
        children = timetable.getchildren()
        for node in children:
            if node.tag == 'h2': break
            timetable.remove(node)

        # Now serialize this section of the tree back into a string,
        # then decode it because Django is going to assume UTF-8.
        return etree.tostring(timetable,
                              pretty_print=True,
                              method='html',
                              encoding='latin1').decode('latin1')

    def official_info(self):
        """A proxy variable for :obj:`self.registrar_info`. Never ever
        access or set that :obj:`self.registrar_info` directly."""

        if not self.registrar_info:
            try:
                self.registrar_info = self.update_official_info()
            except Exception, e:
                self.registrar_info = "Not offered next semester."
            self.save()
        return self.registrar_info

    def get_absolute_url(self):
        return '/courses/' + self.cid + '/'

    class Meta: ordering = ['dep','num']
    class Admin: pass

class BlackBoard(models.Model):
    default_message = """Write comments and messages to other students about the course on this BlackBoard.
    --Joseph Javier Perla"""

    course = models.ForeignKey(Course, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    text = models.TextField(default=default_message)

    def __str__(self):
        return '%s: ...%s' % (str(self.course), self.text[-30:])

    class Admin:
        pass

class Offering(models.Model):
    course = models.ForeignKey(Course)

    professors = models.ManyToManyField(Professor, null=True, blank=True)

    semester = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return '%s %s - %s' % (self.semester, self.year, str(self.course))

    class Meta:
        ordering = ['-year','semester','course']

    class Admin:
        pass

class CrossListManager(models.Manager):
    def courses_in_dep(self, dep):
        courses = []
        cross_lists = CrossList.objects.filter(dep=dep).order_by('num')
        for cross_list in cross_lists:
            courses.append(cross_list.course)
        return courses

class CrossList(models.Model):
    course = models.ForeignKey(Course)
    dep = models.CharField(max_length=10, blank=True)
    num = models.CharField(max_length=30, blank=True)
    objects = CrossListManager()

    def __str__(self):
        return self.course.dep + " " + self.course.num + ": " + self.dep + " " + self.num

    class Admin:
        pass

class Section(models.Model):
    sid = models.CharField(max_length=20, blank=True, primary_key=True)
    offering = models.ForeignKey(Offering)

    required = models.BooleanField(default=False)

    format = models.CharField(max_length=10, blank=True)
    format_number = models.CharField(max_length=10, blank=True)
    format_sub_section = models.CharField(max_length=10, blank=True)
    session = models.CharField(max_length=10, blank=True)

    begins = models.CharField(max_length=10, blank=True)
    ends = models.CharField(max_length=10, blank=True)
    length = models.IntegerField(default=50)

    is_tba = models.CharField(max_length=10, blank=True)

    day1 = models.CharField(max_length=10, blank=True)
    day2 = models.CharField(max_length=10, blank=True)
    day3 = models.CharField(max_length=10, blank=True)
    day4 = models.CharField(max_length=10, blank=True)
    day5 = models.CharField(max_length=10, blank=True)
    days = models.CharField(max_length=10, blank=True)

    building = models.CharField(max_length=30, blank=True)
    room = models.CharField(max_length=30, blank=True)

    estimated_enrollment = models.CharField(max_length=30, blank=True)
    max_enrollment = models.CharField(max_length=30, blank=True)

    section_cancelled = models.CharField(max_length=10, blank=True)
    is_course_published = models.CharField(max_length=10, blank=True)
    is_section_published = models.CharField(max_length=10, blank=True)
    is_closed = models.CharField(max_length=10, blank=True)

    class_stat = models.CharField(max_length=10, blank=True)

    def detail_in_list(self):
        detail = self.format + self.format_number + self.format_sub_section
        if self.begins:
            detail += ': ' + self.begins.lower() + ' - ' + self.ends.lower() + ' ' + self.days
        else:
            detail += ': TBA'
        detail += ' - %s %s' % (self.building, self.room)
        detail += ' <span style="font-size:smaller;">( %s )</span>' % self.sid
        return detail

    def __str__(self):
        return self.offering.course.dep + ' ' + self.offering.course.num + ': ' + self.format + self.format_number + self.format_sub_section

    class Admin:
        pass
