from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField
from storage.models import *

class RegistrationForm(forms.ModelForm):
    cell_number = USPhoneNumberField(label='Cell phone number')
    proxy_email = forms.EmailField(label='Proxy email', required=False)
    dropoff_pickup_time = forms.ModelChoiceField(DropoffPickupTime.objects.all(),
                                                 widget=forms.RadioSelect,
                                                 label="Dropoff/pickup time",
                                                 empty_label=None)
    n_boxes_bought = forms.IntegerField(label='Quantity', widget=forms.TextInput(attrs={'size':'1'}))
    
    BOX_PRICE = "9.40"
    MAX_BOXES = 10
    
    class Meta:
        model=Status
        fields =  ('cell_number',
                   'dropoff_pickup_time', 'n_boxes_bought',
                   'proxy_name', 'proxy_email',)
    
    def clean_n_boxes_bought(self):
        quantity = self.cleaned_data['n_boxes_bought']
        if quantity > self.MAX_BOXES:
            raise forms.ValidationError("Limit %d boxes." % self.MAX_BOXES)
        dp_time = self.cleaned_data['dropoff_pickup_time']
        n_boxes_left = dp_time.n_boxes_total - dp_time.n_boxes_bought
        if quantity > n_boxes_left:
            raise forms.ValidationError("There are only %d boxes available for the time you picked." % n_boxes_left)
        return quantity
    
    def save(self, user, commit=True):
        dp_time = self.cleaned_data['dropoff_pickup_time']
        
        
        form = super(RegistrationForm, self).save(commit=False)
        form.user = user
        form.save()