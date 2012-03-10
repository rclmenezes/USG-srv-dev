from django import forms
from social.models import *
from datetime import datetime, timedelta

goodInputs = ('%m/%d/%Y %I:%M %p','%m/%d/%Y %I:%M%p', '%m/%d/%Y')
    
class EventForm(forms.ModelForm):
    time_start = forms.DateTimeField(label='Start time', input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    time_end = forms.DateTimeField(label='End time', input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    
    class Meta:
        model=Event
        fields = ('entry', 'entry_description', 'time_start', 'time_end', 'title', 'description', 'poster')
        
    def clean_time_start(self):
        time_start = self.cleaned_data['time_start']
        if (time_start - datetime.now()) < timedelta(0):
            raise forms.ValidationError("Event must be in future.")
        return time_start

    def clean_time_end(self):
        time_start = self.cleaned_data.get('time_start')
        if not time_start:
            raise forms.ValidationError("Event must have a valid start time.")

        time_end = self.cleaned_data['time_end']       
        if not time_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (time_end - time_start) < timedelta(0):
            raise forms.ValidationError("Event end time must be after start time.")
        return time_end