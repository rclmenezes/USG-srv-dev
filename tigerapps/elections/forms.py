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
    
    def clean_statement(self):
        statement = self.cleaned_data['statement']
        if not statement:
            raise forms.ValidationError("You must submit a candidate statement.")
        words = [word for word in statement.strip().split() if len(word) > 0]
        if len(words) > 120:
            raise forms.ValidationError("Your statement must have less than 120 words.")
        return statement
