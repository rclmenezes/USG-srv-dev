from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField
from storage.models import *

class RegistrationForm(forms.ModelForm):
    cell_number = USPhoneNumberField(label = 'Cell phone number')
    proxy_email = forms.EmailField(label = 'Proxy email', required=False)
    
    class Meta:
        model=Status
        fields =  ('cell_number',
                   'proxy_name', 'proxy_email',
                   'dropoff_pickup_time')

    #def save(self, user, commit=True):
    #    pass
    '''
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
        '''

