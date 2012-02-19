################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  forms.py
# Info :  central hub of all <forms> using Django models
################################################################

from django import forms
from django.forms.formsets import BaseFormSet
from django.contrib.admin import widgets as adminwidgets
from models import *
#import datetime
from datetime import datetime, timedelta

goodInputs = ('%m/%d/%Y %I:%M %p','%m/%d/%Y %I:%M%p', '%m/%d/%Y')
RSVPInputs = ('%m/%d/%Y',)

class RequiredFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        if not self.forms[0].has_changed():
            raise forms.ValidationError('You are missing a required field.')

class EventForm(forms.ModelForm):
    event_subdescription = forms.CharField(widget=forms.Textarea, label='Subdescription', required=False, max_length=10000)
    event_date_time_start = forms.DateTimeField(label='Start time', input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    event_date_time_end = forms.DateTimeField(label='End time',input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    event_date_rsvp_deadline = forms.DateField(label='RSVP deadline', input_formats=RSVPInputs, required=False, widget=forms.DateInput(format='%m/%d/%Y'))

    class Meta:
        model=Event
        #exclude = ('event_user_last_modified', 'event_cluster', 'event_attendee_count')
        fields = ['event_date_time_start', 'event_date_time_end', 'event_location', 'event_location_details', 'event_date_rsvp_deadline', 'event_max_attendance', 'event_subtitle', 'event_subdescription']

    def clean_event_date_time_start(self):
        event_date_time_start = self.cleaned_data['event_date_time_start']
        if not event_date_time_start:
            raise forms.ValidationError("Event must have a valid start time.")
        if (event_date_time_start - datetime.now()) < timedelta(0):
            raise forms.ValidationError("Event must be in future.")
        return event_date_time_start

    def clean_event_date_time_end(self):
        event_date_time_start = self.cleaned_data.get('event_date_time_start')
        if not event_date_time_start:
            raise forms.ValidationError("Event must have a valid start time.")

        event_date_time_end = self.cleaned_data['event_date_time_end']       
        if not event_date_time_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (event_date_time_end - event_date_time_start) < timedelta(0):
            raise forms.ValidationError("Event end time must be after start time.")
        return event_date_time_end

    def clean_event_date_rsvp_deadline(self):
        event_date_rsvp_deadline = self.cleaned_data['event_date_rsvp_deadline']

        #RSVP deadline is an optional field 
        if not event_date_rsvp_deadline:
            return event_date_rsvp_deadline

        event_date_time_start = self.cleaned_data.get('event_date_time_start')
        if not event_date_time_start:
            raise forms.ValidationError("Event must have a valid start time.")
        
        event_date_time_end = self.cleaned_data.get('event_date_time_end')
        if not event_date_time_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (event_date_rsvp_deadline - event_date_time_start.date()) > timedelta(0):
            raise forms.ValidationError("The RSVP deadline cannot be after the event start.")
        if (event_date_rsvp_deadline - event_date_time_end.date()) > timedelta(0):
            raise forms.ValidationError("The RSVP deadline cannot be after the event end.")
        if (event_date_rsvp_deadline - date.today()) < timedelta(0):
            raise forms.ValidationError("The RSVP deadline must be in the future.")
        return event_date_rsvp_deadline

class SingleEventForm(forms.ModelForm):
    event_date_time_start = forms.DateTimeField(label='Start time', input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    event_date_time_end = forms.DateTimeField(label='End time', input_formats=goodInputs, widget=forms.DateTimeInput(format='%m/%d/%Y %I:%M %p'))
    event_date_rsvp_deadline = forms.DateField(label='RSVP deadline', input_formats=RSVPInputs, widget=forms.DateTimeInput(format='%m/%d/%Y'), required=False)
    
    class Meta:
        model=Event
        exclude = ('event_user_last_modified', 'event_cluster', 'event_subtitle', 'event_subdescription', 'event_attendee_count')  
        fields = ['event_date_time_start', 'event_date_time_end', 'event_location', 'event_location_details', 'event_date_rsvp_deadline', 'event_max_attendance']    

    def clean_event_date_time_start(self):
        event_date_time_start = self.cleaned_data['event_date_time_start']
        if (event_date_time_start - datetime.now()) < timedelta(0):
            raise forms.ValidationError("Event must be in future.")
        return event_date_time_start

    def clean_event_date_time_end(self):
        event_date_time_start = self.cleaned_data.get('event_date_time_start')
        if not event_date_time_start:
            raise forms.ValidationError("Event must have a valid start time.")

        event_date_time_end = self.cleaned_data['event_date_time_end']       
        if not event_date_time_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (event_date_time_end - event_date_time_start) < timedelta(0):
            raise forms.ValidationError("Event end time must be after start time.")
        return event_date_time_end

    def clean_event_date_rsvp_deadline(self):
        event_date_rsvp_deadline = self.cleaned_data['event_date_rsvp_deadline']

        #RSVP deadline is an optional field 
        if not event_date_rsvp_deadline:
            return event_date_rsvp_deadline

        event_date_time_start = self.cleaned_data.get('event_date_time_start')
        if not event_date_time_start:
            raise forms.ValidationError("Event must have a valid start time.")
        
        event_date_time_end = self.cleaned_data.get('event_date_time_end')
        if not event_date_time_end:
            raise forms.ValidationError("Event must have a valid end time.")

        if (event_date_rsvp_deadline - event_date_time_start.date()) > timedelta(0):
            raise forms.ValidationError("The RSVP deadline cannot be after the event start.")
        if (event_date_rsvp_deadline - event_date_time_end.date()) > timedelta(0):
            raise forms.ValidationError("The RSVP deadline cannot be after the event end.")
        if (event_date_rsvp_deadline - date.today()) < timedelta(0):
            raise forms.ValidationError("The RSVP deadline must be in the future.")
        return event_date_rsvp_deadline

class EventClusterForm(forms.ModelForm):
    cluster_description = forms.CharField(widget=forms.Textarea, label='Description', max_length=10000)
    
    class Meta:
        model=EventCluster
        exclude = ('cluster_user_created')
        fields = ['cluster_title', 'cluster_description', 'cluster_category', 'cluster_features', 'cluster_image', 'cluster_rsvp_enabled', 'cluster_board_enabled', 'cluster_notify_boardpost']

class EditUserForm(forms.ModelForm):
   class Meta:
      model=CalUser
      exclude = ('user_netid', 'user_pustatus', 'user_dept', 'user_recently_viewed_events', 'user_last_login', 'user_recent_views')


class AddMessageForm(forms.ModelForm):
   class Meta:
      model=BoardMessage
      exclude = ('boardmessage_eventcluster', 'boardmessage_time_posted', 'boardmessage_poster')
