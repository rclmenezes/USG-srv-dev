from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from my.models import *
from BeautifulSoup import BeautifulSoup
import sys, urllib2
from groups.models import *
from groups.forms import WidgetSettingsForm
from groups.globalsettings import SITE_URL as groups_url
from card.models import *
from myapps.models import *
from my.views import proxyURL
from cal.models import Event
from datetime import datetime, date, timedelta
from django.db import connection, transaction
import json
current_module = sys.modules[__name__]

def get_myapp(request, relationID):
    # Sanity check/security measure
    try:
        relation = MyAppRelation.objects.get(relationID=relationID)
    except MyAppRelation.DoesNotExist:
        raise Http404
        
    myapp = relation.myapp
    settings = relation.settings
    # If redirect
    if myapp.myappType == u'R':
        return HttpResponseRedirect(myapp.link)
    if myapp.myappType == u'A':
        raise Http404

    return getattr(current_module, myapp.viewName)(request, settings)

def unicorn(request, settings):
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/unicorn.html')
    else:
        return render_to_response('my/myapps/no.html')

def hamster(request, settings):
    return render_to_response('my/myapps/hamster.html')
    
def deflation(request, settings):
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/deflation.html')
    else:
        return render_to_response('my/myapps/no.html')
    
def lorem(request, settings):
    return render_to_response('my/myapps/lorem.html')
    
def usg(request, settings):
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/usg_m.html')
    else:
        return render_to_response('my/myapps/usg_s.html')

def groups(request, settings):
    # Get settings
    show_posts = None
    posts_on_page = None
    for setting in settings.all():
        if setting.name == 'show_posts':
            show_posts = setting
        elif setting.name == 'posts_on_page':
            posts_on_page = setting
    if not show_posts:
        show_posts = Setting(value='A',name='show_posts')
        show_posts.save()
        settings.add(show_posts)
    if not posts_on_page:
        posts_on_page = Setting(value='7',name='posts_on_page')
        posts_on_page.save()
        settings.add(posts_on_page)
        
    # Change settings page
    if 'settings' in request.GET and bool(request.GET['settings']):
        if request.method == 'POST':
            form = WidgetSettingsForm(request.POST)
            if form.is_valid():
                show_posts.delete()
                posts_on_page.delete()
                settings.clear()
                show_posts = Setting(value=form.cleaned_data['show_posts'],name='show_posts')
                show_posts.save()
                settings.add(show_posts)
                posts_on_page = Setting(value=form.cleaned_data['posts_on_page'],name='posts_on_page')
                posts_on_page.save()
                settings.add(posts_on_page)
        else:
            form = WidgetSettingsForm()
            if 'M' in request.GET and bool(request.GET['M']):
                return render_to_response('my/myapps/groups_settings_m.html',{'show_posts':show_posts.value,'posts_on_page':posts_on_page.value,'form':form})
            else:
                return render_to_response('my/myapps/groups_settings_s.html',{'show_posts':show_posts.value,'posts_on_page':posts_on_page.value,'form':form})
    
    # Get posts from db
    if show_posts.value == 'S':
        affil = Membership.objects.filter(student__netid__exact=request.user.username).values('group')
        entries = Entry.objects.filter(group__in=affil)[:int(posts_on_page.value)]
        feed = groups_url+'feeds/students/'+request.user.username
    else:
        entries = Entry.objects.all()[:int(posts_on_page.value)]
        feed = groups_url+'feeds/latest'

    # feed page
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/groups_m.html',{'entries':entries,'groups_url':groups_url,'feed':feed})
    else:
        return render_to_response('my/myapps/groups_s.html',{'entries':entries,'groups_url':groups_url,'feed':feed})

def card(request, settings):
    # Get member object for user
    mem = Member.objects.filter(netid__exact=request.user.username)

    # Get meals from db
    completeExchanges = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__host=mem))
    completeExchanges2 = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__guest=mem))
    completeExchanges.extend(completeExchanges2) 
    hostExchanges = Exchange.objects.filter(meal_2=None, meal_1__host=mem)
    guestExchanges = Exchange.objects.filter(meal_2=None, meal_1__guest=mem)

    # render page
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/card_m.html',{'hostExchanges': hostExchanges,'guestExchanges': guestExchanges,'completeExchanges': completeExchanges,})
    else:
        return render_to_response('my/myapps/card_s.html',{'hostExchanges': hostExchanges,'guestExchanges': guestExchanges,'completeExchanges': completeExchanges,})


def prince(request, settings):
    if 'M' in request.GET and bool(request.GET['M']):
        soup = BeautifulSoup(str(proxyURL("http://www.dailyprincetonian.com/")))
        widget = soup.find('div', {'class': 'widget_image'})
        picture_list = []
        
        # Slide show
        for i in widget.findAllNext('td'):
            picture = {}
            picture['link'] = i.a['href']
            picture['src'] = i.a.img['src']
            picture['name'] = i.find('div', {'class': 'caption'}).string.strip()
            picture_list.append(picture)

        # No slide show
        if len(picture_list) == 0:
            picture = {}
            widget_object = widget.find('div', {'class': 'widget_object'})
            picture['link'] = widget_object.a['href']
            picture['src'] = widget_object.a.img['src']
            picture['name'] = widget.find('div', {'class': 'caption'}).string.strip()
            picture_list.append(picture)
            
        return render_to_response('my/myapps/prince_m.html', {'json': json.dumps(picture_list)})
    else:
        return render_to_response('my/myapps/prince_s.html')

def get_schedule_by_netid(netid):
    cursor = connection.cursor()
    
    cursor.execute("SELECT title, chron_order FROM terms")
    current_term = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM timetable WHERE term='" + str(current_term) + "' AND netid='" + netid + "'")
    timetable = cursor.fetchone()
    
    cursor.execute("SELECT course FROM timetable_course WHERE timetable_id='" + str(timetable[0]) + "'")
    courses = cursor.fetchall()
    
    return courses
    
def search_courses(course_id):
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM terms")
    current_term = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM offerings WHERE term_id='" + str(current_term) + "'")# AND course_id='" + str(course_id) + "'")
    courses = cursor.fetchone()

    return courses

def tigermag(request, settings):
    #return HttpResponse(search_courses(41173))
    #return HttpResponse(get_schedule_by_netid("georgiev"))
        
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/tigermag_m.html')
    else:
        return render_to_response('my/myapps/tigermag_s.html')
        
def weather(request, settings):
    if 'M' in request.GET and bool(request.GET['M']):
        return HttpResponse("Medium view not done yet.")
    else:
        return HttpReponse("Not ready yet.")
        
def usg_movies(request, settings):
    today = datetime.today()
    movies = USG_Movie.objects.filter(start__lte=today, end__gte=today)
    if 'M' in request.GET and bool(request.GET['M']):
        return render_to_response('my/myapps/movies_m.html', {'movies': movies})
    else:
        return render_to_response('my/myapps/movies_s.html', {'movies': movies})
    '''
    today = date.today()
    usg_movies = USG_Movie.objects.filter(start__lte=today).filter(end__gte=today)
    for movie in usg_movies:
        soup = BeautifulSoup(str(proxyURL(movie.imdbLink)))
        title = str(soup.find('h1', {'itemprop': 'name'}))
        ratingValue = str(soup.find('span', {'itemprop': 'ratingValue'}))
        poster = str(soup.find('img', {'itemprop': 'image'})['src'])
        return HttpResponse(title + "<br/>" + ratingValue + "<img height=200 src=\"" + poster + "\"/>")
        #soup = BeautifulSoup(f.read())
        #return HttpResponse(soup.prettify())
    '''
    
def cal(request, settings):
    now = datetime.now()
 
    event_list = Event.objects.filter(event_date_time_end__gte=now).order_by('event_date_time_start')[:10]
    image_list = []
    
    if 'M' in request.GET and bool(request.GET['M']):
        for event in event_list:
            if event.event_cluster.cluster_image:
                picture = {}
                picture['link'] =  event.get_absolute_url()
                picture['name'] = event.event_cluster.cluster_title
                picture['src'] = event.event_cluster.cluster_image
                image_list.append(event)
        #return render_to_response('my/myapps/cal_test.html', {'image_list': image_list, 'event_list': event_list})
        return render_to_response('my/myapps/cal_m.html', {'image_list': image_list, 'event_list': event_list})
    else:
        return render_to_response('my/myapps/cal_s.html')