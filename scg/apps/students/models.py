from django.db import models
from django.contrib.auth.models import User
from apps.courses.models import Course, Offering, Section

class MyCourseManager(models.Manager):
    def get_my_courses(self, user, semester, year):
        #mycourses = MyCourse.objects.filter(user=request.user, offering__semester=NEXT_SEMESTER, offering__year=NEXT_YEAR)
        mycourses = MyCourse.objects.filter(user=user, offering__semester=semester,)
        courses = []
        for mycourse in mycourses:
            courses.append(mycourse.offering.course)
        return courses

class MyCourse(models.Model):
    user = models.ForeignKey(User)
    offering = models.ForeignKey(Offering)
    objects = MyCourseManager()

    def __str__(self):
        return '%s: %s' % (str(self.user), str(self.offering))

    #class Meta:
    #    ordering = ['offering']

    class Admin:
        list_display = ('user', 'offering',)

class MySection(models.Model):
    mycourse = models.ForeignKey(MyCourse)
    section = models.ForeignKey(Section)

    def __str__(self):
        return '%s - %s' % (str(self.mycourse), str(self.section))

    #class Meta:
    #    ordering = ['offering']

    class Admin:
        list_display = ('mycourse', 'section',)

class RecentCoursesManager(models.Manager):
    def popular_courses(self, max_courses=20):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT rc.course_id, COUNT(*)
            FROM students_recentcourses rc
            GROUP BY course_id
            ORDER BY COUNT(*) DESC, last_view DESC
        """)
        result_list = []
        for row in cursor.fetchall()[0:max_courses]:
            result_list.append(Course.objects.get(cid=row[0]))
        return result_list

    def recent_courses(self, user, max_courses=20):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM (
                SELECT rc.course_id, cc.dep, cc.num
                FROM courses_course cc, students_recentcourses rc
                WHERE rc.user_id = """ + str(user.id) + """
                AND cc.cid = rc.course_id
                ORDER BY last_view DESC
                LIMIT """ + str(max_courses) + """
            ) AS tbl
            ORDER BY tbl.dep, tbl.num
        """
        )
        result_list = []
        for row in cursor.fetchall():
            result_list.append(Course.objects.get(cid=row[0]))
        return result_list

class RecentCourses(models.Model):
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    last_view = models.DateTimeField(auto_now=True)
    objects = RecentCoursesManager()

    def __str__(self):
        return str(self.user) + ": " + str(self.course)

    class Meta:
        ordering = ['-last_view']

    class Admin:
        list_display = ('user', 'course', 'last_view',)

class RecentDepartmentManager(models.Manager):
    def recent_departments(self, user, max_departments=6):
        rds = RecentDepartments.objects.filter(user=user)[0:max_departments]
        result_list = []
        for rd in rds:
            result_list.append(rd.department)
        result_list.sort()
        return result_list


class RecentDepartments(models.Model):
    user = models.ForeignKey(User)
    department = models.CharField(max_length=30)
    last_view = models.DateTimeField(auto_now=True)
    objects = RecentDepartmentManager()

    def __str__(self):
        return str(self.user) + ': ' + self.department

    class Meta:
        ordering = ['-last_view']

    class Admin:
        pass

class StudentDepartment(models.Model):
    user = models.OneToOneField(User,
                                related_name='department',
                                primary_key=True)
    department = models.CharField(max_length=30, blank=True)

    #class Meta:
    #    ordering = ['-user']

    def __str__(self):
        return str(self.user) + ': ' + self.department

    class Admin:
        list_display = ('user', 'department')

