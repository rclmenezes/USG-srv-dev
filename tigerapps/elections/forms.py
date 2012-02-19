from django import forms
from django.forms.formsets import BaseFormSet
from django.contrib.admin import widgets as adminwidgets
from models import *
from django.forms import ModelChoiceField
#import datetime
from datetime import datetime, timedelta

class CandidateForm(forms.ModelForm):   
    class Meta:
        model=Candidate
        fields = ['office', 'name', 'statement', 'headshot']