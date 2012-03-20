import itertools
from django import forms

from apps.courses.models import Course, THIS_YEAR
from apps.courses.views import departments
from apps.professors.models import Professor
from apps.reviews.models import GRADE_CHOICES, TERM_CHOICES

# I am deeply sorry.
YEARS = [(y,y) for y in [''] + range(2004, int(THIS_YEAR) + 1)]

class DecimalField(forms.RegexField):
   def __init__(self, max_length=None, min_length=None, error_message=None, required=True, widget=None, label=None, initial=None):
        forms.RegexField.__init__(self, '^[0-9]+(\.[0-9]+)?$', max_length, min_length, error_message, required, widget, label, initial)

class RequiredForm(forms.Form):
    cid = forms.ChoiceField(choices=[('','')] + [(c.cid, unicode(c))
                                                 for c in Course.objects.all()],
                            widget=forms.Select(attrs={'style':'width: 200px'}))
    pid = forms.ChoiceField(choices=[('','')] + [(p.pid, unicode(p))
                                                 for p in Professor.objects.all()],
                            widget=forms.Select(attrs={'style':'width: 200px'}))
    department = forms.ChoiceField(choices=[(d,d) for d in [''] + departments])
    year = forms.ChoiceField(choices=YEARS)
    term = forms.ChoiceField(choices=[('','')] + TERM_CHOICES)


def get_choices(first, last):
    choices = []
    for (i, choice) in enumerate(GRADE_CHOICES):
        if i == 0:
            choices.append((choice[0],choice[1] + ' ' + first))
        elif i == len(GRADE_CHOICES) - 1:
            choices.append((choice[0],choice[1] + ' ' + last))
        else:
            choices.append((choice[0],choice[1]))
    return choices

MIN_LENGTH = 50
text_widget = forms.Textarea(attrs={'cols':'60','rows':'1'})

class CourseForm(forms.Form):
    q1_choices = [('','')] + get_choices('Stellar','Poor')
    q2_choices = [('',''), ('4.0','A lot less'), ('3.0','A little less'), ('2.0','Average'), ('1.0','A little more'), ('0.0','A lot more')]
    q3_choices = [('','')] + get_choices('Insist on your friend enrolling','Discourage your friend from taking it')

    q1 = DecimalField(widget=forms.Select(choices=q1_choices), required=False)
    q2 = DecimalField(widget=forms.Select(choices=q2_choices), required=False)
    q3 = DecimalField(widget=forms.Select(choices=q3_choices), required=False)
    comment = forms.CharField(widget=text_widget, required=False)
    advice = forms.CharField(widget=text_widget, required=False)

    def clean_comment(self):
        if len(self.cleaned_data['comment']) < MIN_LENGTH and self.cleaned_data['comment'] != '':
            raise forms.ValidationError(u'The narrative descriptions are the most valuable parts of the reviews.  Please make sure that you add enough to your review to be helpful.')

        self.cleaned_data['comment'] = self.cleaned_data['comment'].encode('utf-8')
        return self.cleaned_data['comment']

    def clean_advice(self):
        if len(self.cleaned_data['advice']) < MIN_LENGTH and self.cleaned_data['advice'] != '':
            raise forms.ValidationError(u'The narrative descriptions are the most valuable parts of the reviews.  Please make sure that you add enough to your review to be helpful.')

        self.cleaned_data['advice'] = self.cleaned_data['advice'].encode('utf-8')
        return self.cleaned_data['advice']

    def clean(self):
        if '' not in self.cleaned_data.itervalues() or set(self.cleaned_data.values()) == set(['']):
            return self.cleaned_data
        else:
            raise forms.ValidationError(u'If you fill out a course review, be sure to fill out the whole review.')


class ProfessorForm(forms.Form):
    q1_choices = [('','')] + get_choices('Outstanding','Unacceptable')
    q2_choices = [('','')] + get_choices('Flexible hours/loved seeing students',"Professor wasn't able to/didn't want to meet")
    q3_choices = [('','')] + get_choices('Completely Engaging','Sorely Lacking')
    q4_choices = [('','')] + get_choices('Absolutely Fantastic','Truly Disappointing')

    q1 = DecimalField(widget=forms.Select(choices=q1_choices), required=False)
    q2 = DecimalField(widget=forms.Select(choices=q2_choices), required=False)
    q3 = DecimalField(widget=forms.Select(choices=q3_choices), required=False)
    q4 = DecimalField(widget=forms.Select(choices=q4_choices), required=False)
    comment = forms.CharField(widget=text_widget, required=False)

    def clean_comment(self):
        if len(self.cleaned_data['comment']) < MIN_LENGTH and self.cleaned_data['comment'] != '':
            raise forms.ValidationError(u'The narrative descriptions are the most valuable parts of the reviews.  Please make sure that you add enough to your review to be helpful.')

        self.cleaned_data['comment'] = self.cleaned_data['comment'].encode('utf-8')
        return self.cleaned_data['comment']

    def clean(self):
        if '' not in self.cleaned_data.itervalues() or set(self.cleaned_data.values()) == set(['']):
            return self.cleaned_data
        else:
            raise forms.ValidationError(u'If you fill out a professor review, be sure to fill out the whole review.')



