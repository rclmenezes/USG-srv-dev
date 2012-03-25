from card.models import *
from django.contrib import admin
from adminsites import cardAdmin
from django.forms.models import BaseInlineFormSet

def mark_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
mark_active.short_description = 'Mark members as active'

def mark_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
mark_inactive.short_description = 'Mark members as inactive'

class MemberAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name','netid','year','club','access','is_active')
    search_fields = ('last_name','first_name','netid','puid')
    list_filter = ('is_active','access','year','club')
    actions = (mark_active, mark_inactive)
    def queryset(self, request):
        qs = super(MemberAdmin, self).queryset(request)
        return qs.exclude(first_name__exact='x',last_name__exact='x')

class ClubAdmin(admin.ModelAdmin):
    fields = ('name','account')
    search_fields = ('name',)
    readonly_fields = ('account',)

class ExchangeAdmin1Inline(admin.TabularInline):
    model = Exchange
    fk_name = 'meal_1'
    extra = 0
    raw_id_fields = ('meal_2',)

class ExchangeAdmin2Inline(admin.TabularInline):
    model = Exchange
    fk_name = 'meal_2'
    extra = 0
    raw_id_fields = ('meal_1',)

class MealAdmin(admin.ModelAdmin):
    list_display = ('date','meal_type','checker','host','guest')
    search_fields = ('checker__netid','host__netid','guest__netid')
    list_filter = ('date','meal_type')
    inlines = (ExchangeAdmin1Inline,ExchangeAdmin2Inline,)

class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('meal_1','meal_2')

admin.site.register(Member, MemberAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.register(Meal, MealAdmin)
admin.site.register(Exchange, ExchangeAdmin)
cardAdmin.register(Member, MemberAdmin)
cardAdmin.register(Club, ClubAdmin)
cardAdmin.register(Meal, MealAdmin)
cardAdmin.register(Exchange, ExchangeAdmin)
