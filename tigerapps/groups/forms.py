from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from models import *
from django.forms.extras.widgets import SelectDateWidget
from stdimage import StdImageField
from django.forms.models import inlineformset_factory
from cal.models import Event

class GroupProfileForm(ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description','netid','categories', 'site', 'email', 'image', 'show_members')

class NewGroupForm(ModelForm):
    class Meta:
        model = GroupRequest
        exclude = ['supplicant', 'ticket']
        extra = 0
    def __init__(self, *args, **kwargs):
        super(NewGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Group Name'
        self.fields['netid'].label = 'Group Netid'

class RenewGroupForm(ModelForm):
    confirm = forms.BooleanField()
    class Meta:
        model = Group
        fields = ('name','description','categories', 'site', 'email')

class ReactivateGroupForm(ModelForm):
    reason_for_reactivation = forms.CharField(max_length=5000, widget=forms.Textarea)
    confirm = forms.BooleanField()
    class Meta:
        model = Group
        fields = ('name', 'description','categories', 'site', 'email')
            
class PromoteForm(ModelForm):
    promote = forms.BooleanField(initial=True, required=False)
    class Meta:
        model=Membership
        fields = ('student', 'title', 'officer_order')
        extra = 0

class AccountForm(ModelForm):
    feed_notifications = forms.CharField(max_length=1,help_text='Send me an email when one of my groups posts to their feed', widget = forms.Select(choices=NOTIFICATION_CHOICES))
    mship_notifications = forms.CharField(max_length=1,help_text='Send me an email if my membership status changes in a group', label='Membership notifications', widget = forms.Select(choices=NOTIFICATION_CHOICES))
    message_notifications = forms.CharField(max_length=1,help_text='Send me an email when I recieve a message', widget = forms.Select(choices=NOTIFICATION_CHOICES))
    request_notifications = forms.CharField(max_length=1,help_text='Send me an email when students request to become members of a group where I am an officer', widget = forms.Select(choices=NOTIFICATION_CHOICES))
    class Meta:
        model = Student
        exclude = ['netid','invite_notifications']
        extra = 0

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = ['group', 'pub_date']
        extra = 0
    def __init__(self,*args,**kwargs):
        super(EntryForm, self).__init__(*args, **kwargs) 
        if self.instance:
            events = Event.objects.filter(event_cluster__cluster_user_created__user_netid__in=Membership.objects.filter(group=self.instance.group,type='O').values('student__netid'))
            event_field = self.fields['event'].widget
            event_choices = [] 
            event_choices.append(('', '---------')) 
            if events:
                for event in events: 
                    event_choices.append((event.event_id, event)) 
            event_field.choices = event_choices 

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100,required=False,label='')
    category = forms.ModelChoiceField(empty_label='All Categories',queryset=Category.objects.all(),required=False,label='')

class MshipSettingsForm(ModelForm):
    display = forms.CharField(max_length=1,help_text='Who can see my name on this group\'s member list',required=False,widget = forms.Select(choices=DISPLAY_CHOICES))
    mship_notifications = forms.BooleanField(help_text='Send me an email when membership status changes for this group', label='Membership notifications', required=False, initial=True)
    class Meta:
        model = Membership
        extra = 0
        fields = ['title','officer_order','display','feed_notifications', 'mship_notifications','message_notifications','request_notifications']

class MshipRequestForm(ModelForm):
    mship_notifications = forms.BooleanField(help_text='Send me an email when membership status changes for this group', label='Membership Notifications', required=False,initial=True)
    class Meta:
        model = MembershipRequest
        extra = 0
        exclude = ['group', 'student']

class MessageForm(ModelForm):
    class Meta:
        model = Message
        extra = 0
        exclude = ['pub_date', 'author', 'group', 'unread']

class MessageCommentForm(ModelForm):
    class Meta:
        model = MessageComment
        extra = 0
        fields = ['text']

class SearchGroupMessageForm(forms.Form):
    search = forms.CharField(max_length=100,required=False,label='Title:')
#    date = forms.DateField(required=False,initial=None,label='Date:',widget=SelectDateWidget())
    date = forms.DateField(required=False,initial=None,label='Date:')

class SearchApproveForm(forms.Form):
    f_name = forms.CharField(max_length=100,required=False,label='First Name:')
    l_name = forms.CharField(max_length=100,required=False,label='Last Name:')
    netid = forms.CharField(max_length=10,required=False,label='Netid:')
    year = forms.IntegerField(required=False,label='Year:')

class SearchMemberForm(forms.Form):
    f_name = forms.CharField(max_length=100,required=False,label='First Name:')
    l_name = forms.CharField(max_length=100,required=False,label='Last Name:')
    netid = forms.CharField(max_length=10,required=False,label='Netid:')
    year = forms.IntegerField(required=False,label='Year:')
    rank = forms.CharField(max_length=100,required=False,label='Rank:',
                           widget=forms.Select(choices=
                                               (
                ('N','------'),('M','Member'),('O','Officer'),
                )))

class MembershipAdminFormSet(BaseInlineFormSet):
    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            qs = super(MembershipAdminFormSet, self).get_queryset().filter(type__in=['O','M'])[:15]
            self._queryset = qs
        return self._queryset

class WidgetSettingsForm(forms.Form):
    show_posts = forms.ChoiceField(choices=(('A','From all groups'),('S','Only from groups I\'m affiliated with')))
    posts_on_page = forms.ChoiceField(choices=(('3','3'),('5','5'),('7','7'),('10','10'),('12','12'),('15','15'),))
