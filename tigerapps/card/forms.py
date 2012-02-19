from django.contrib.auth import authenticate, login, logout
from card.models import *
from django import forms
from django.forms.models import ModelForm
from datetime import date
from django.contrib.auth.models import User

class AddMemberForm(ModelForm):
    class Meta:
        model = Member
        exclude = ['access','is_active','club']
        extra = 0
    def clean_year(self):
        year = self.cleaned_data.get('year')
        now = date.today()
        if len(str(year)) != 4 or int(year) < int(now.year):
            raise forms.ValidationError('Year must be year of future graduation in yyyy format')
        return year
    def clean_netid(self):
        netid = self.cleaned_data.get('netid')
        if not netid.islower() or not netid.isalnum():
            raise forms.ValidationError('Invalid netid format')
        return netid
    def clean_puid(self):
        puid = self.cleaned_data.get('puid')
        if len(str(puid)) != 9:
            raise forms.ValidationError('Invalid PUID format')
        return puid

class ModMemberForm(ModelForm):
    class Meta:
        model = Member
        exclude = ['netid','club','puid']
    def clean_year(self):
        year = self.cleaned_data.get('year')
        now = date.today()
        if len(str(year)) != 4 or int(year) < int(now.year):
            raise forms.ValidationError('Year must be year of future graduation in yyyy format')
        return year

class AddMealForm(ModelForm):
    host = forms.CharField(max_length=10,label='Host Netid')
    guest = forms.CharField(max_length=10,label='Guest Netid')
    date = forms.DateField(initial=date.today().strftime('%m/%d/%Y'),widget=forms.DateInput(format = '%m/%d/%Y'))
    meal_type = forms.ChoiceField(choices=MEAL_TUPLE_CHOICES,label='Meal')
    class Meta:
        model = Meal
        exclude = ['checker']
    def clean_host(self):
        host_netid = self.cleaned_data.get('host')
        checker_netid = self.instance.checker
        c = Member.objects.get(netid=checker_netid)
        try:
            h = Member.objects.get(netid=host_netid)
        except:
            raise ValidationError('Host not registered with card')
        if h.club != c.club:
            raise ValidationError('Host must be a member of this club')
        return h
    def clean_guest(self):
        guest_netid = self.cleaned_data.get('guest')
        checker_netid = self.instance.checker
        c = Member.objects.get(netid=checker_netid)
        try:
            g = Member.objects.get(netid=guest_netid)
        except:
            raise ValidationError('Guest not registered with card')
        if g.club == c.club:
            raise ValidationError('Guest cannot be a member of this club')
        return g
    
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(max_length=25,widget=forms.PasswordInput(render_value=False))
    new_password = forms.CharField(max_length=25,widget=forms.PasswordInput(render_value=False))
    retype_password = forms.CharField(max_length=25,widget=forms.PasswordInput(render_value=False))
    def clean_new_password(self):
        new = self.cleaned_data.get('new_password')
        if len(new) < 5:
            raise ValidationError('Password must be at least 5 characters in length')
        return new
    def clean_retype_password(self):
        new = self.cleaned_data.get('new_password')
        retype = self.cleaned_data.get('retype_password')
        if new != retype:
            raise ValidationError('Retyped password did not match new password')
        return retype

class ChangeEmailForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']
