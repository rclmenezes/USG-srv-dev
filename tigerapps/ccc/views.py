from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.core.mail import send_mail
from ccc.models import *
from ccc.forms import *

def index(request):
    return render_to_response('ccc/index.html')

def post(request, postTitle):
    post = Post.objects.get(title=postTitle)
    return render_to_response('ccc/post.html', {'post': post})
  
  
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
    # Get hours already logged
    hours = 0
    for log in LogCluster.objects.filter(user=request.user):
        hours += log.hours
    
    log_cluster_form = LogClusterForm()
    if request.method == 'POST':
        log_cluster_form = LogClusterForm(request.POST)
        if log_cluster_form.is_valid():
            log = log_cluster_form.save(commit=False)
            log.user = request.user
            log.save()
            return render_to_response('ccc/confirm.html', {'log': log})
    name = request.user
    return render_to_response('ccc/log_hours.html', {'log_cluster_form': log_cluster_form, 'hours': hours, 'name': name})
    
# For non-blog posts    
def view_404(request):
    return render_to_response('elections/404.html')
    
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
    #return render_to_response('ccc/top.html', {'volunteers': volunteers})
  
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
