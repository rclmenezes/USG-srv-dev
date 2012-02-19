from django import forms
from ttrade.models import *
        
class ListingForm(forms.ModelForm):
    class Meta:
        model=Listing
        fields = ('category', 'method', 'title', 'description', 'picture', 'price')
