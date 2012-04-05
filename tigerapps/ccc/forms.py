from django import forms
from ccc.models import *
from django.db.models import F
import datetime

DateInputs = ('%m/%d/%Y',)
ccc_start = datetime.date(month=10, day=29, year=2011)
 
class LogClusterForm(forms.ModelForm):
    date = forms.DateField(label='Date', input_formats=DateInputs, widget=forms.DateInput(format='%m/%d/%Y'))
    #date_end = forms.DateField(label='End Date', input_formats=DateInputs, widget=forms.DateInput(format='%m/%d/%Y'))
    
    class Meta:
        model=LogCluster
        fields =  ['year', 'res_college', 'eating_club', 'date', 'project', 'hours']
    
    def clean_date(self):
        date = self.cleaned_data['date']
        if not date:
            raise forms.ValidationError("Event must have a valid start time.")
        if (datetime.date.today() - date) < datetime.timedelta(0):
            raise forms.ValidationError("Event must be in the past.")
        return date
    
    '''
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
    
    def save(self, user, force_insert=False, force_update=False, commit=True):
        #save into GroupHours as well
        hours = self.cleaned_data['hours']
        date = self.cleaned_data.get('date')
        month = datetime.date(date.year, date.month, 1)
        group_types = ['year', 'res_college', 'eating_club']
        
        for group_type in group_types:
            group_name = self.cleaned_data.get(group_type)
            if group_name:
                try:
                    entry = GroupHours.objects.get(group=group_name, month=month)
                except GroupHours.DoesNotExist, e:
                    entry = GroupHours(group=group_name, month=month, hours=0)
                entry.hours += hours
                if commit:
                    entry.save()
        
        log_entry = super(LogClusterForm, self).save(commit=False)
        log_entry.user = user
        log_entry.save()


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model=ProjectRequest
        fields = ['project', 'description', 'coordinator_name', 'coordinator_email']
