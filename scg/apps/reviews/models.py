from django.db import models
from django.contrib.auth.models import User
from apps.courses.models import Course
from apps.professors.models import Professor

TERM_CHOICES = [
    ('S', 'Spring'),
    ('F', 'Fall'),
]

GRADE_CHOICES = [
    (4.0, 'A+'),
    (4.0, 'A'),
    (3.7, 'A-'),
    (3.3, 'B+'),
    (3.0, 'B'),
    (2.7, 'B-'),
    (2.3, 'C+'),
    (2.0, 'C'),
    (1.7, 'C-'),
    (1.0, 'D'),
    (0.0, 'F'),
]

class CourseReview(models.Model):
    id = models.AutoField('ID', primary_key=True)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    course = models.ForeignKey(Course)
    user = models.ForeignKey(User)

    year = models.CharField(max_length=10, blank=True, null=True)
    term = models.CharField(max_length=2, blank=True, null=True, choices=TERM_CHOICES)

    professor = models.ForeignKey(Professor, null=True, blank=True)

    q1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, )
    q2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, )
    q3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, )
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    comment = models.TextField(blank=True, null=True)
    advice = models.TextField(blank=True, null=True)

    def get_workload(self):
        WORKLOAD_CHOICES = ((0.00, 'A lot more'),
                            (1.00, 'A little more'),
                            (2.00, 'Average'),
                            (3.00, 'A little less'),
                            (4.00, 'A lot less'))
        import math
        for num,word in WORKLOAD_CHOICES:
            if float(self.q2) <= num:
                return word
        return WORKLOAD_CHOICES[2][1]

    def get_absolute_url(self):
        return '/reviews/course/%s/' % self.course.cid

    def __str__(self):
        return str(self.course) + ' by ' + str(self.user)

    # force_insert: http://groups.google.com/group/django-users/browse_thread/thread/2471efd68d56ad59
    def save(self, *args, **kwargs):
        self.average = self.q3
        super(CourseReview, self).save(*args, **kwargs) # Call the "real" save() method.
        self.update_course_review_stats()

    def delete(self):
        super(CourseReview, self).delete() # Call the "real" delete() method.
        self.update_course_review_stats()

    def update_course_review_stats(self):
        c = self.course
        reviews = CourseReview.objects.filter(course=c)
        c.num_reviews = len(reviews)
        gpa = 0.0
        for r in reviews:
            gpa += float(r.average)

        try: gpa = gpa / len(reviews)
        except ZeroDivisionError: gpa = 0.0

        c.gpa = str(gpa)
        c.save()


    class Meta:
        ordering = ['-year','term','-id']

    class Admin:
        fields = (
            (None, {'fields': ('course','user','year','term','professor','q1','q2','q3','average','comment','advice')}),
            ('Static', {'fields':('updated','added')}),
        )
        list_display = ('course', 'user', 'year', 'term', 'added')
        search_fields = ['user','course']

# Create your models here.
class ProfessorReview(models.Model):
    id = models.AutoField('ID', primary_key=True)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    course = models.ForeignKey(Course, blank=True, null=True)
    user = models.ForeignKey(User)

    year = models.CharField(max_length=10, blank=True, null=True)
    term = models.CharField(max_length=2, blank=True, null=True, choices=TERM_CHOICES)

    professor = models.ForeignKey(Professor)

    q1 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    q2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    q3 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    q4 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    comment = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return '/reviews/professor/%s/' % self.professor.pid

    def __str__(self):
        return str(self.professor) + ' by ' + str(self.user)

    class Meta:
        ordering = ['-year','term']

    def save(self, *args, **kwargs):
        self.average = self.q4
        super(ProfessorReview, self).save(*args, **kwargs) # Call the "real" save() method.
        self.update_professor_review_stats()

    def delete(self):
        super(ProfessorReview, self).delete() # Call the "real" delete() method.
        self.update_professor_review_stats()

    def update_professor_review_stats(self):
        p = self.professor
        reviews = ProfessorReview.objects.filter(professor=p)
        p.num_reviews = len(reviews)
        gpa = 0.0
        for r in reviews:
            gpa += float(r.average)

        try: gpa = gpa / len(reviews)
        except ZeroDivisionError: gpa = 0.0

        p.gpa = str(gpa)
        p.save()

    class Admin:
        list_display = ('professor', 'user', 'year', 'term', 'added')
