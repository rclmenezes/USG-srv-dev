from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from elections.models import *
from dsml import *
from django.contrib.auth.models import User
from elections.forms import *
from random import shuffle

def home(request):
    now = datetime.now()
    try: 
        election = Election.objects.latest('deadline')
    except Election.DoesNotExist:
        election = None
        
    if election == None:
        return HttpResponse("Site is not properly set up. You need to create an election in <a href=\"/admin/\">the admin page</a>.")
    elif election.end < now:
        return render_to_response('elections/end.html')
    elif election.deadline < now:
        return statements(request)
    else:
        return signup(request, election)
        
def statements(request):
    election = Election.objects.latest('deadline')
    
    try:
        runoff = Runoff.objects.get(election=election)
        return runoffs(request, runoff)
    except Runoff.DoesNotExist:
        pass
    
    officeCandidates = {}
    for office in election.offices.all():
        officeCandidates[office] = []
        for candidate in Candidate.objects.filter(office=office, election=election):
            officeCandidates[office].append(candidate)
        shuffle(officeCandidates[office])
    return render_to_response('elections/statements.html', {'officeCandidates': officeCandidates})
    
@login_required
def remove(request):
    if request.method == "POST" and 'netid' in request.POST and request.POST['netid'] == request.user.username:
        candidate = Candidate.objects.get(netid=request.POST['netid'])
        candidate.delete()
        return render_to_response('elections/remove.html')
    return HttpResponseRedirect("http://elections.tigerapps.org/")
    
@login_required    
def signup(request, election):
    if election is None:
        now = datetime.now()
        try: 
            election = Election.objects.latest('deadline')
        except Election.DoesNotExist:
            election = None
            return HttpResponse("Site is not properly set up. You need to create an election in <a href=\"/admin/\">the admin page</a>.")
    
    now = datetime.now()        
    #if election.deadline < now:
    #    return statements(request)
    
    changes = register = False
    
    # Get candidate's information
    user_info = gdi(request.user.username)
    try:
        start = datetime(day=1, month=8, year=int(user_info['puclassyear'])-4)
        elapsed = datetime.now() - start
        if elapsed.days < 365*1:
            year = 'FR'
            officeSet = Office.objects.filter(freshman_eligible=True)
        elif elapsed.days < 365*2:
            year = 'SO'
            officeSet = Office.objects.filter(sophomore_eligible=True)
        else:
            year = 'JU'
            officeSet = Office.objects.filter(junior_eligible=True)
        
        if request.user.username == 'rmenezes':
            officeSet = Office.objects.all()   
        
    except KeyError: # For USG account
        return render_to_response('elections/nope.html')

    if len(officeSet) == 0:
        return render_to_response('elections/nope.html')
       
    try: # if candidate already exists
        candidate = Candidate.objects.get(netid=request.user.username, election=election)
        if request.method == 'POST':
            candidateForm = CandidateForm(request.POST, request.FILES, instance=candidate)
            if candidateForm.is_valid(): #Edit candidate
                candidateForm.save()
                changes = True
        else:
            candidateForm = CandidateForm(instance=candidate)

    except Candidate.DoesNotExist:
        candidate = None
        if request.method == 'POST':
            candidate = Candidate(election=election, netid=request.user.username, year=year)
            candidateForm = CandidateForm(request.POST, request.FILES, instance=candidate)
            if candidateForm.is_valid():
                candidate = candidateForm.save()
                register = True
            else:
                candidate = None
        else:
            try:
                candidateForm = CandidateForm(initial={'name': user_info['displayName']})
            except KeyError: # In case DSML server dies
                candidateForm = CandidateForm()

    candidateForm.fields["office"].queryset = officeSet # Sets default
    
    officeList = {}
    for office in election.offices.all():
        officeList[office] = len(Candidate.objects.filter(office=office, election=election))
    
    return render_to_response('elections/register.html', {'user': request.user, 'candidateForm': candidateForm, 'changes': changes, 'register': register, 'candidate': candidate, 'election': election, 'officeList': officeList})
    
def runoffs(request, runoff):
    '''
    try: 
        election = Election.objects.latest('deadline')
    except Election.DoesNotExist:
        election = None
    try:
        runoff = Runoff.objects.get(election=election)
    except:
        pass
    '''
    
    election = runoff.election
    
    officeCandidates = {}
    for office in election.offices.all():
        officeCandidates[office] = []
        for candidate in runoff.candidates.filter(office=office):
            officeCandidates[office].append(candidate)
        shuffle(officeCandidates[office])
    return render_to_response('elections/statements.html', {'officeCandidates': officeCandidates})