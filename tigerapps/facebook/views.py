from django.http import *
from render import render_to_response
from auth import *
from models import *
from sets import Set
from decorators import login_required
import urllib
import copy
from django.utils.datastructures import SortedDict


@login_required	
def home(request):
	return profile(request,request.session['user_data'].user_netid)

@login_required	
def profile(request, netid):
	try:
		user = User.objects.get(user_netid = netid)
	except:
		user = User.objects.filter(user_netid = netid)[1]
	dict = {}
	dict['user'] = user
	dict['bday_month'] = user.user_birthday.strftime("%B")
	dict['bday_year'] = user.user_birthday.year
	dict['bday_day'] = user.user_birthday.day
	
	if current_user(request) != user:
		pv = PageView()
		
		pv.view_viewer = current_user(request)
		pv.view_profile = user
		pv.view_datetime = datetime.now()
		
		pv.save()
	
	dict['view_count'] = PageView.objects.filter(view_profile = user).count()
	
	searchurl = "/search?"
	for key in FIELDMAP:
		cmd = '''val = user.%s''' % FIELDMAP[key]
		exec cmd
		dict['url'+FIELDMAP[key]] =  searchurl+urllib.urlencode({'f0':key,'q0':val})
	
	try:
		dict['major'] = DEPT_CODE[user.user_dept]
	except:
		dict['major'] = user.user_dept
	dict['abbrev_college'] = user.user_rescollege.replace(" Residential College", "")
	try:
		dict['full_state'] = STATE_CODE[user.user_homestate]
	except:
		dict['full_state'] = user.user_homestate
		
	dict['related_rescol'] = User.objects.filter(user_rescollege=user.user_rescollege).order_by('?')[:5]
	if user.user_dept in DEPT_CODE:
		dict['related_major'] = User.objects.filter(user_dept=user.user_dept).order_by('?')[:5]
	
	dict['birthday'] = searchurl+urllib.urlencode({'f0':'Birthday','q0':('-%d-%d' % (user.user_birthday.month,user.user_birthday.day))})
	dict['birthyear'] = searchurl+urllib.urlencode({'f0':'Birthday','q0':('%d-' % (user.user_birthday.year))})
	
	return render_to_response(request,'profile.html',dict)
	
def profileEdit(request, netid):
	pass
	
def min(x,y):
	if x<y:
		return x
	else:
		return y

#@login_required	
def search(request):
	max_page = 50
	dict = {}
	disabled = ['Suffix','Mailbox']
	keys = filter(lambda x: x not in disabled, FIELDMAP.keys())
	dict['fields'] = FIELDMAP.keys()
	dict['ac_field'] = keys
	if request.method == 'GET' and len(request.GET) > 1:
		page = int(request.GET.get('p', 1))
		results,fields = searchResults(request)
		dict['results_count'] = results.count()		
		dict['results'] = results[((page-1)*max_page):min(((page)*max_page),results.count())]
		dict['result_start_count'] = ((page-1)*max_page)+1
		dict['result_end_count'] = min(((page)*max_page),results.count())
		dict['selected_fields'] = fields
		if (page)*max_page < results.count():
			ndict = copy.deepcopy(request.GET)
			ndict['p'] = page+1
			dict['page_next'] = urllib.urlencode(ndict)
		if (page-1)*max_page > 0:
			pdict = copy.deepcopy(request.GET)
			pdict['p'] = page-1
			dict['page_prev'] = urllib.urlencode(pdict)
	return render_to_response(request,'search.html',dict)

def searchResults(request):
	qdict = SortedDict()
	fields = []
	for i in range(0,len(request.GET.keys())/2):	
		if ('f'+str(i)) in request.GET and ('q'+str(i)) in request.GET:
			qdict[request.GET[('f'+str(i))]] = request.GET[('q'+str(i))]
			fields.append((('f'+str(i)),(request.GET[('f'+str(i))]),('q'+str(i)),(request.GET[('q'+str(i))])))
	results = User.objects.all();
	for k in qdict:
		field = FIELDMAP[k]
		kwargs = {'%s__%s' % (field, 'contains'): qdict[k], }
		results =  results.filter(**kwargs)
	return (results,fields)
	
def autocomplete(request, fieldname):
	dict = {}
	if fieldname in FIELDMAP:
		dict['items'] = sorted(getListOfVals(FIELDMAP[fieldname]))
	return render_to_response(request,'jsonlist',dict)

def getListOfVals(field):
	return Set(User.objects.values_list(field,flat=True))	

def toolshed(request):
	return HttpResponseRedirect('/search?f0=Department&q0=WWS')

# def photoEdit(request)
# 	user = current_user(request)
# 	
# 	if request.method == 'POST':
#     upload_form = ProfileForm(request.POST, request.FILES)
		#photo_file = request.FILES['photo']
# 
#     if upload_form.is_valid():
#         upload_form.save()
#         return HttpResponseRedirect('/')	
# 
#     else:
#        upload_form = ProfileForm(instance=request.user.profile)
