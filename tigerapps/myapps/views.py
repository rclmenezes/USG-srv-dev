from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from my.models import MyApp, MyAppRelation, Setting
from django.core.mail import send_mail
from BeautifulSoup import BeautifulSoup
import sys, urllib2
from django.utils import simplejson
from groups.models import *
from groups.forms import WidgetSettingsForm
from groups.globalsettings import SITE_URL as groups_url
from card.models import *
from myapps.models import *
from my.views import proxyURL
from cal.models import Event
from datetime import datetime, date, timedelta
from django.db import connection, transaction
current_module = sys.modules[__name__]

@login_required
def get_myapp(request, relationID, location, settings):
    # Sanity check/security measure
    try:
        relation = MyAppRelation.objects.get(relationID=relationID)
    except MyAppRelation.DoesNotExist:
        raise Http404
        
    myapp = relation.myapp
    # If redirect
    if myapp.myappType == u'R':
        return HttpResponseRedirect(myapp.link)
    if myapp.myappType == u'A':
        raise Http404

    if settings:
        return getattr(current_module, myapp.viewName + "_settings")(request, location, relation.settings)
    else:
        return getattr(current_module, myapp.viewName)(request, location, relation.settings)

def unicorn(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/unicorn.html')
    else:
        return render_to_response('my/myapps/no.html')

def hamster(request, location, settings):
    return render_to_response('my/myapps/hamster.html')
    
def deflation(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/deflation.html')
    else:
        return render_to_response('my/myapps/no.html')
    
def lorem(request, location, settings):
    return render_to_response('my/myapps/lorem.html')
    
def usg(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/usg_m.html')
    else:
        return render_to_response('my/myapps/usg_s.html')

def groups(request, location, settings):
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
        
    # Get posts from db
    if show_posts.value == 'S':
        affil = Membership.objects.filter(student__netid__exact=request.user.username).values('group')
        entries = Entry.objects.filter(group__in=affil)[:int(posts_on_page.value)]
        feed = groups_url+'feeds/students/'+request.user.username
    else:
        entries = Entry.objects.all()[:int(posts_on_page.value)]
        feed = groups_url+'feeds/latest'

    # feed page
    if location == 'M':
        return render_to_response('my/myapps/groups_m.html',{'entries':entries,'groups_url':groups_url,'feed':feed})
    else:
        return render_to_response('my/myapps/groups_s.html',{'entries':entries,'groups_url':groups_url,'feed':feed})

def groups_settings(request, location, settings):
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
        if location == 'M':
            return render_to_response('my/myapps/groups_settings_m.html',{'show_posts':show_posts.value,'posts_on_page':posts_on_page.value,'form':form})
        else:
            return render_to_response('my/myapps/groups_settings_s.html',{'show_posts':show_posts.value,'posts_on_page':posts_on_page.value,'form':form})

def card(request, location, settings):
    # Get member object for user
    mem = Member.objects.filter(netid__exact=request.user.username)

    # Get meals from db
    completeExchanges = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__host=mem))
    completeExchanges2 = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__guest=mem))
    completeExchanges.extend(completeExchanges2) 
    hostExchanges = Exchange.objects.filter(meal_2=None, meal_1__host=mem)
    guestExchanges = Exchange.objects.filter(meal_2=None, meal_1__guest=mem)

    # render page
    if location == 'M':
        return render_to_response('my/myapps/card_m.html',{'hostExchanges': hostExchanges,'guestExchanges': guestExchanges,'completeExchanges': completeExchanges,})
    else:
        return render_to_response('my/myapps/card_s.html',{'hostExchanges': hostExchanges,'guestExchanges': guestExchanges,'completeExchanges': completeExchanges,})


def prince(request, location, settings):
    if location == 'M':
        soup = BeautifulSoup(str(proxyURL("http://www.dailyprincetonian.com/")))
        widget = soup.find('div', {'class': 'widget_image'})
        picture_list = []
        
        # Slide show
        for i in widget.findAllNext('td'):
            picture = {}
            picture['link'] = "http://dailyprincetonian.com" + i.a['href']
            picture['src'] = i.a.img['src']
            picture['name'] = i.find('div', {'class': 'caption'}).string.strip()
            picture_list.append(picture)

        # No slide show
        if len(picture_list) == 0:
            picture = {}
            widget_object = widget.find('div', {'class': 'widget_object'})
            picture['link'] = "http://dailyprincetonian.com" + widget_object.a['href']
            picture['src'] = widget_object.a.img['src']
            picture['name'] = widget.find('div', {'class': 'caption'}).string.strip()
            picture_list.append(picture)
            
        return render_to_response('my/myapps/prince_m.html', {'json': simplejson.dumps(picture_list)})
    else:
        return render_to_response('my/myapps/prince_s.html')

def ice_courses(request, location, settings):
    netid = request.user.username
    schedule = str(proxyURL("http://ice.tigerapps.org/php/load.php?q=timetable&id=" + netid))
    index = schedule.index("{")
    schedule = schedule[index:]
    timetables = simplejson.loads(schedule)['data']
    terms = {}
    
    for timetable in timetables:
        term = timetable['term']
        courses = timetable['courses']
        day_list = []
        for i in range(0,5):
            day_list.append([])
        term = ""
        
        for course in courses:
            i = 0
            indices = course['indices'].split()
            fields = ['lecture', 'seminar', 'class', 'lab', 'precept', 'studio', 'drill', 'ear']
            for field in fields:
                try:
                    if indices[i] == -1:
                        course[field] = course[field]
                    else:
                        slot = {}
                        slot['title'] = course['title']
                        slot['type'] = field
                        term = course['term']
                        
                        # Parsing this form: 0~P01@TTh 19:30:00 20:20:00
                        info = course[field].split(',')[int(indices[i])].replace("Th","H")
                        space_split = info.split('@')[1].split()
                        slot['sort_time'] = space_split[1].split(":")[0]
                        slot['time'] = str(humanize_hour(space_split[1].split(":")[0]) + ":" + space_split[1].split(":")[1])+"-"+str(humanize_hour(space_split[2].split(":")[0]) + ":" + space_split[2].split(":")[1])
                        
                        days = space_split[0]
                        weekdays = [('M', 'Monday', 0),('T', 'Tuesday', 1),('W','Wednesday', 2),('H','Thursday', 3),('F','Friday', 4)]
                        for weekday in weekdays:
                            if days.find(weekday[0]) != -1:
                                day_list[weekday[2]].append(slot)
                        i += 1
                except:
                    pass
        terms[term] = day_list      
        # To get location, use this url:
        # http://ice.tigerapps.org/php/load.php?q=enroll&data={{ cid }}&term={{ termnum }}&key={{ seconds since epoch }}
        # http://ice.tigerapps.org/php/load.php?q=enroll&data=002060&term=1122&key=1325953689
    
    now = date.today()
            
    if location == 'M':
        return render_to_response('my/myapps/ice_m.html', {"json": simplejson.dumps(terms), "weekday": now.weekday()})
    else:
        return render_to_response('my/myapps/ice_s.html', {"json": simplejson.dumps(terms), "weekday": now.weekday()})  

def humanize_hour(hour):
    if int(hour) > 12:
        return str(int(hour) - 12)
    return hour
    
def tigermag(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/tigermag_m.html')
    else:
        return render_to_response('my/myapps/tigermag_s.html')
        
def weather(request, location, settings):
    if location == 'M':
        return HttpResponse("Medium view not done yet.")
    else:
        return HttpReponse("Not ready yet.")
        
def usg_movies(request, location, settings):
    today = datetime.today()
    movies = USG_Movie.objects.filter(start__lte=today, end__gte=today)
    if location == 'M':
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
    
def cal(request, location, settings):
    now = datetime.now()
 
    event_list = Event.objects.filter(event_date_time_end__gte=now).order_by('event_date_time_start')[:10]
    image_list = []
    
    if location == 'M':
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
        
def anon_email(request, location, settings):
    error = False
    message = "Please be respectful when using this service."
    if request.method == 'GET' and 'submit' in request.GET:
        if not 'netid' in request.GET or len(request.GET['netid']) == 0 or len(request.GET['netid']) > 8:
            error = True
            message = "Netid length must be between one and eight characters."
            
        elif not 'subject' in request.GET or len(request.GET['subject']) == 0:
            error = True
            message = "Cannot send with empty subject line."
            
        elif not 'content' in request.GET or len(request.GET['content']) == 0: 
            error = True
            message = "Cannot send empty email."
            
        else:
            from_email = "anonymous@tigerapps.org"
            to_email = [request.GET['netid'] + "@princeton.edu"]
            subject = request.GET['subject']
            content = request.GET['content'] + "\n\nThis is an anonymous letter sent through MyPrinceton. This service is intended to provide anonymous, constructive feedback. We apologize if this service has been misused."
            
            try:
                #return HttpResponse(str(to_email) + "\n" + subject + "\n" + content)
                send_mail(subject, content, from_email, to_email)
                message = "Success! Message sent."
            except:
                error = True
                message = "Something went wrong."
    
    if location == 'M':
        return render_to_response('my/myapps/anon_email_m.html', {'error': error, 'message': message})
    else:
        return render_to_response('my/myapps/anon_email_s.html', {'error': error, 'message': message})
        
def tigertrade(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/ttrade_m.html')
    else:
        return render_to_response('my/myapps/ttrade_s.html')
        
def pfml(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/pfml_m.html')
    else:
        return render_to_response('my/myapps/pfml_s.html')
        
def printer(request, location, settings):
    if location == 'M':
        return render_to_response('my/myapps/printer_m.html')
    else:
        return render_to_response('my/myapps/printer_s.html')