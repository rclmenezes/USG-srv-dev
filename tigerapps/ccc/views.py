from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.mail import send_mail
from ccc.models import *
from ccc.forms import *
from django_cas.decorators import login_required, user_passes_test
import operator, simplejson

def index(request):
    return render_to_response('ccc/index.html')

def view_404(request):
    return HttpResponseNotFound(render_to_string('elections/404.html'))


def blog(request):
    postList = Post.objects.filter(in_blog=True).order_by('posted').reverse()
    paginator = Paginator(postList, 1)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
  
    # If page request (9999) is out of range, deliver last page of results.
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    
    return render_to_response('ccc/blog.html', {"posts": posts})

# For non-blog posts    
def post(request, postTitle):
    postTitle = postTitle.replace('_', ' ')
    post = get_object_or_404(Post, title=postTitle, in_blog=False)
    return render_to_response('ccc/post.html', {'post': post})


@login_required
def log_choices(request):
    # Get the account (or create one)
    hours = 0
    for log in LogCluster.objects.filter(is_approved=True, user=request.user):
        hours += log.hours
        
    return render_to_response('ccc/log-choose.html', {'hours': hours})
    
@login_required
def project_request(request):
    project_request_form = ProjectRequestForm()
    if request.method == 'POST':
        project_request_form = ProjectRequestForm(request.POST)
        if project_request_form.is_valid():
            project_request = project_request_form.save(commit=False)
            project_request.user = request.user
            project_request.save()
            
            # EMAIL ALEX HERE
            send_mail('[CCC] New Project Request', 
                      "Hi,\n\nThere's been a new project request. Go to http://ccc.tigerapps.org/admin/ccc/projectrequest/ to approve it (click on its checkbox and click approve under \"Actions\").\n\nBest,\n\nTigerApps Staff", 
                      'do-not-reply@tigerapps.org',
                       ["ccc@princetonusg.com"], 
                       fail_silently=True)
            
            return render_to_response('ccc/confirm.html', {'request': True})
    
    return render_to_response('ccc/project_request.html', {'project_request_form': project_request_form})
   
@login_required
def log_hours(request):
    hours = LogCluster.objects.get_user_hours(user=request.user)
    
    log_cluster_form = LogClusterForm()
    if request.method == 'POST':
        log_cluster_form = LogClusterForm(request.POST)
        if log_cluster_form.is_valid():
            log = log_cluster_form.save(request.user, commit=True)
            return render_to_response('ccc/confirm.html', {'log': log})
    netid = request.user
    return render_to_response('ccc/log_hours.html', {'log_cluster_form': log_cluster_form, 'user_hours': hours, 'user_netid': netid})
    
@login_required
def leaderboard(request):
    user_hours = LogCluster.objects.get_user_hours(user=request.user)

    if 'month' in request.GET:
        in_month, in_year = request.GET['month'].split('-')
        month = datetime.date(int(in_year), int(in_month), 1)
    else:
        today = datetime.date.today()
        month = datetime.date(today.year, today.month, 1)

    #for rendering the table
    total_hours = 0
    groups_dict = {'Classes': YEAR_CHOICES,
                   'Residential Colleges': RES_COLLEGE_CHOICES,
                   'Eating Clubs': EATING_CLUB_CHOICES}
    hours_dict = {'Classes': [],
                  'Residential Colleges': [],
                  'Eating Clubs': []}
    for group_type, group_names in groups_dict.iteritems():
        for group_name,other in group_names:
            try:
                entry = GroupHours.objects.get(group=group_name, month=month)
            except GroupHours.DoesNotExist, e:
                entry = GroupHours(group=group_name, month=month, hours=0)
                entry.save()
            total_hours += entry.hours
            hours_dict[group_type].append((entry.group, entry.hours))
        hours_dict[group_type] = sorted(hours_dict[group_type], key=operator.itemgetter(1), reverse=True)

    #for rendering the choices of month
    months = GroupHours.objects.get_months()
    month_choices = tuple((m.strftime("%m-%Y"), m.strftime("%B %Y"), m==month) for m in months)

    return render_to_response('ccc/leaderboard.html', {'hours_dict': hours_dict, 'user_hours': user_hours, 'total_hours': total_hours,
                                                       'month_choices': month_choices})


#---------------------------------------------------------------------------------------
#hours_admin related

@login_required
@user_passes_test(lambda u: u.is_staff)
def hours_admin(request):
    today = datetime.date.today()
    month = datetime.date(today.year, today.month, 1)
    top_users = LogCluster.objects.get_month_hours(month)

    #for rendering the choices of month
    months = GroupHours.objects.get_months()
    month_choices = tuple((m.strftime("%m-%Y"), m.strftime("%B %Y")) for m in months)

    return render_to_response('ccc/hours_admin.html', {'month_choices':month_choices})

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_user_hours(request):
    '''
    Returns html of the user's hours. Called when admin user searches
    for a NETID at /hours_admin/
    '''
    try:
        netid = request.GET['netid']
        try:
            user = User.objects.get(username=netid)
        except User.DoesNotExist, e:
            return HttpResponse("User %s could not be found" % netid)
        hours = LogCluster.objects.get_user_hours(user=user)
        return HttpResponse("%s: %d hours" % (netid, hours))
    except Exception, e:
        return HttpResponse("Invalid input: %s" % e)

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_month_group_hours(request):
    '''
    Returns HTML for hours each user logged in a month for a particular group, in
    sorted order of # of hours logged.
    '''
    try:
        in_month, in_year = request.GET['month'].split('-')
        month = datetime.date(int(in_year), int(in_month), 1)
        if 'group' in request.GET and 'groupType' in request.GET:
            group = request.GET['group']
            top_hours = LogCluster.objects.get_month_hours(month, request.GET['group'], request.GET['groupType'])
        else:
            group = None
            top_hours = LogCluster.objects.get_month_hours(month)
        return HttpResponse(render_to_string('ccc/hours_admin_mg_hours.html', {'top_hours':top_hours,
            'month':month.strftime('%B %Y'),
            'group':group}))
    except Exception, e:
        return HttpResponse("Invalid input: %s" % e)

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_user_awards(request):
    '''
    Returns json of all users that logged over X hours since date Y without
    receiving an award for X hours since date Y
    '''

    try:
        hours = int(request.GET['hours'])
        date_str = [int(d) for d in request.GET['date'].split('/')]
        date = datetime.date(date_str[2], date_str[0], date_str[1])
    except Exception, e:
        return HttpResponse("Invalid input: %s" % e)

    try:
        users = User.objects.filter(logcluster__date__gte=date).\
            annotate(num_hours=models.Sum('logcluster__hours')).\
            filter(num_hours__gte=hours).\
            exclude(award__hours=hours, award__date__gte=date)
    except Exception, e:
        return HttpResponse("1st query exception: %s" % e)

    response_json = simplejson.dumps([(u.username, u.num_hours) for u in users])
    return HttpResponse(response_json, content_type="application/javascript")

@login_required
@user_passes_test(lambda u: u.is_staff)
def post_user_awards(request):
    '''
    Log into `Award` model that user X got an award today for logging Y hours. Does
    no checking that the user actually has logged Y hours.
    '''

    try:
        hours = int(request.POST['hours'])
        netid = request.POST['netid']
    except Exception, e:
        return HttpResponse("Invalid input: %s" % e)
    try:
        user = User.objects.get(username=netid)
    except User.DoesNotExist, e:
        return HttpResponse("User %s could not be found" % netid)

    today = datetime.date.today()
    try:
        award = Award.objects.get(user=user, hours=hours, date=today)
        return HttpResponse("Warning: Award was already logged today")
    except Award.DoesNotExist, e:
        award = Award(user=user, hours=hours, date=datetime.date.today())
        award.save()

    return HttpResopnse("Successfully logged: User %s, Hours %d, Date %s" % (user.username, hours, date.strftime("%M/%d/%Y")))



#---------------------------------------------------------------------------------------
#not sure what these are for

def all_hours(request):
    # Nicer than a tuple, methinks
    class Volunteer:
        def __init__(self, user, hours):
            self.user = user
            self.hours = hours
    
    volunteers = []
    logs = LogCluster.objects.order_by('user__username')
    prev_user = None
    prev_hours = 0
    for log in logs:
        user = log.user
        if user != prev_user:
            if prev_user is not None:
                volunteers.append(Volunteer(prev_user, prev_hours))
                #value += prev_user.username + " " + str(prev_hours) + "<br/>"
            prev_user = user
            prev_hours = log.hours
        else:
            prev_hours += log.hours
    volunteers = sorted(volunteers, key=lambda volunteer: -volunteer.hours)
    
    value = ""
    for volunteer in volunteers:
        value += volunteer.user.username + " " + str(volunteer.hours) + "<br/>"

    return HttpResponse(value)


def top(request):
    # Nicer than a tuple, methinks
    class Volunteer:
        def __init__(self, user, hours):
            self.user = user
            self.hours = hours
    
    volunteers = []
    logs = LogCluster.objects.order_by('user__username')
    prev_user = None
    prev_hours = 0
    for log in logs:
        user = log.user
        if user != prev_user:
            if prev_user is not None:
                volunteers.append(Volunteer(prev_user, prev_hours))
                #value += prev_user.username + " " + str(prev_hours) + "<br/>"
            prev_user = user
            prev_hours = log.hours
        else:
            prev_hours += log.hours
    volunteers = sorted(volunteers, key=lambda volunteer: -volunteer.hours)[:20]

    return render_to_response('ccc/top.html', {'volunteers': volunteers})


'''
OLD CODE BEFORE THEY CHANGED THE SPECS >:|
@login_required  
def register(request):
    user = request.user

    try:
        participant = Participant.objects.get(user=request.user)
    except Participant.DoesNotExist:
        user_info = gdi(user.username)
        user.first_name = user_info['givenName']
        user.last_name = user_info['sn']
        user.save()
        participant = Participant(user=user, team=None)
        participant.save()
    
    return render_to_response('ccc/register.html')

################# AJAX VIEWS ##################

def check_name(request):
    if 'name' in request.POST:
        name = request.POST['name']
    else:
        raise Http404
        
    try:
        team = Team.objects.get(name=name)
        return HttpResponse("false")
    except Team.DoesNotExist:
        if len(name) == 0:
            return HttpResponse("empty")
        return HttpResponse("true")
        
def search_team(request):
    if not request.is_ajax():
        raise Http404
        
    if request.POST['search-field'] == 'P':
        searchList = Participant.objects.all()
        field = 'name'
    elif request.POST['search-field'] == 'T':
        searchList = Team.objects.all()
        field = 'user'
    else:
        raise Http404
        
    if 'search_query' in request.POST:
        query = request.POST['query']
        if query != "" and query.strip() != "": 
            searchList = searchList.filter(get_query(query, [field]))
    else:
        query = None
    
    if request.POST['search-field'] == 'P':
        result_list = []
        for result in searchList:
            result_list.append(result.user.username)

    if request.POST['search-field'] == 'T':
        result_list = []
        for result in searchList:
            result_list.append(result.name)
        
    response_dict = {'data': result_list}
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    
    '''
