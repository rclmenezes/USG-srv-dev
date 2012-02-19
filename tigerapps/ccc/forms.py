from django import forms
from ccc.models import *
from datetime import date, timedelta

DateInputs = ('%m/%d/%Y',)
ccc_start = date(month=10, day=10, year=2011)
 
class LogClusterForm(forms.ModelForm):
    date_start = forms.DateField(label='Start Date', input_formats=DateInputs, widget=forms.DateInput(format='%m/%d/%Y'))
    date_end = forms.DateField(label='End Date', input_formats=DateInputs, widget=forms.DateInput(format='%m/%d/%Y'))
    
    class Meta:
        model=LogCluster
        fields = ['date_start', 'date_end', 'project', 'hours']
    
    def clean_date_start(self):
        date_start = self.cleaned_data['date_start']
        if not date_start:
            raise forms.ValidationError("Event must have a valid start time.")
        if (date.today() - date_start) < timedelta(0):
            raise forms.ValidationError("Event must be in the past.")
        return date_start

    def clean_date_end(self):
        date_start = self.cleaned_data.get('date_start')
        if not date_start:
            raise forms.ValidationError("Event must have a valid start time.")

        date_end = self.cleaned_data['date_end']       
        if not date_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (date_end - date_start) < timedelta(0):
            raise forms.ValidationError("Event end time must be after start time.")
        return date_end
    
    '''    
    def clean(self):
        cleaned_data = self.cleaned_data
        date_start = self.cleaned_data['date_start']
        date_end = self.cleaned_data['date_end']
        
        if date_start < ccc_start:
            raise forms.ValidationError("Project must have started after October 10th, 2011")
        if date_end > datetime.date.today():
            raise forms.ValidationError("Project must have already ended")
        if date_end < date_start:
            raise forms.ValidationError("Date end must be after date start")
    '''
        
class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model=ProjectRequest
        fields = ['project', 'description', 'coordinator_name', 'coordinator_email']
