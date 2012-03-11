from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from my.models import *
from django.http import Http404
from django.core import serializers
from search import *
import sys, urllib2, datetime

@login_required
def getPage(request, orderNo): 
    netid = request.user.username
    try:
        account = Account.objects.get(netid=netid)
    except Account.DoesNotExist:
        account = Account(netid=netid)
        account.save()
        account.create()
    
    if orderNo is None:
        orderNo = 0
        
    page = get_object_or_404(account.pages, orderNo=orderNo)
    pages = len(account.pages.all())
    colList = page.getMyApps()
    pageBar = account.getPageBar(page)
    return render_to_response('my/home.html', {'colList': colList, 'pageBar': pageBar, 'orderNo': orderNo, 'pages': pages})
  
### AJAX VIEWS ###  
  
@login_required
def saveMyApps(request, orderNo):
    if request.method != 'POST' or not request.is_ajax():
        raise Http404
    
    account = get_object_or_404(Account, netid=request.user.username)
    page = get_object_or_404(account.pages, orderNo=orderNo)
    
    data = simplejson.loads(request.POST['data'])
    items = data['items']
    compare = page.myapps.all()
    for item in items:
        relationID = int(item['id'])
        relation = MyAppRelation.objects.get(relationID=relationID)
        compare = compare.exclude(relationID=relationID)
        relation.column = item['column']
        relation.collapsed = item['collapsed']
        relation.sort_no = int(item['order'])
        relation.save()
    # Checks if we threw something away   
    for relation in compare:
        page.myapps.remove(relation)
        for setting in relation.settings.all():
            setting.delete()
        relation.delete()
    page.save()
    return HttpResponse("success")
    
# Proxy for RSS feeds :p 
def proxy(request):
    #if not request.is_ajax():
    #    raise Http404

    if request.method == 'GET' and 'url' in request.GET:
        url = request.GET['url']
    else:
        raise Http404

    return HttpResponse(proxyURL(url))
    
def proxyURL(url):
    try:
       cache = PageCache.objects.get(url=url)
       if cache.posted + datetime.timedelta(minutes=5) > datetime.datetime.now():
           return HttpResponse(cache.contents)
    except PageCache.DoesNotExist:
        cache = PageCache(url=url)

    cache.contents = urllib2.urlopen(url).read()
    cache.posted = datetime.datetime.now()
    cache.save()
    return str(cache.contents)
    
@login_required   
def refreshApps(request):
    if not request.is_ajax():
        raise Http404
    
    myappList = MyApp.objects.all().order_by('name').reverse()
    if 'query' in request.GET:
        query = request.GET['query']
        if query != "" and query.strip() != "": 
            myappList = myappList.filter(get_query(query, ['name', 'description']))
    else:
        query = None

    select= request.GET['select']    
    if select != 'Al':
        myappList = myappList.filter(category=select)

    data = serializers.serialize('json', myappList, fields=('name','description'))

    response_dict = {}
    response_dict.update({'data': data})
    response_dict.update({'select': select})
    response_dict.update({'query': query})
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    
@login_required
def removePage(request):
    if not request.is_ajax():
        raise Http404
    
    account = get_object_or_404(Account, netid=request.user.username)
    if 'orderNo' in request.POST and len(account.pages.all()) > 1:
        orderNo = int(request.POST['orderNo'])
        page = get_object_or_404(account.pages, orderNo=orderNo)
        for relation in page.myapps.all():
            for settings in relation.settings.all():
                settings.delete()
            relation.delete()
        page.delete()

        for page in account.pages.all():
            if page.orderNo > orderNo:
                page.orderNo = page.orderNo - 1
                page.save()
        account.save()
        return HttpResponse("success")
    raise Http404

@login_required
def changePageName(request, orderNo):
    if not request.is_ajax():
        raise Http404
    
    account = get_object_or_404(Account, netid=request.user.username)
    if 'name' in request.POST:
        page = get_object_or_404(account.pages, orderNo=orderNo)
        page.name = request.POST['name']
        page.save()
        return HttpResponse("success")
    raise Http404

### MODAL VIEWS ###

@login_required        
def addMyApp(request, orderNo, colID):
    if request.user.is_staff:
        myappList = MyApp.objects.all().order_by('name')
    else:
        myappList = MyApp.objects.exclude(myappType='T').order_by('name')
    account = get_object_or_404(Account, netid=request.user.username)
    
    if colID == None:
        colID = "N"
    
    if orderNo == None:
        orderNo = len(account.pages.all()) - 1
    page = account.pages.get(orderNo=orderNo)
    
    # Get categories for search and appends amount in each category
    choices = MYAPP_CATEGORIES
    categories = []
    categories.append(('Al', 'All Categories', len(myappList)))
    for choice in choices:
        categories.append((choice[0], choice[1], len(myappList.filter(category=choice[0]))))
    
    return render_to_response('my/addMyApp.html', {'myappList': myappList, 'categories': categories, 'page': page, 'colID': colID})
 
@login_required
def confirmMyApps(request, orderNo, colID):
    account = get_object_or_404(Account, netid=request.user.username)
    page = get_object_or_404(account.pages, orderNo=orderNo)
    for key in request.POST:
        myapp = MyApp.objects.get(myappID=int(request.POST[key]))
        left = len(page.myapps.filter(column="L"))
        right = len(page.myapps.filter(column="R"))
        middle = len(page.myapps.filter(column="M"))
        if colID == "N":
            # Get approriate column (by preference of app maker and/or by column w/ least)
            if myapp.preference == 'M' or (myapp.preference == 'N' and middle < left and middle < right):
                column = 'M'
            else:
                if left < right:
                    column = 'L'
                else:
                    column = 'R'
        else:
            column = colID
            
        if column == 'L':
            sort_no = left
        elif column == 'R':
            sort_no = right
        else:
            sort_no = middle

        relation = MyAppRelation(myapp=myapp, collapsed=False, column=column, sort_no=sort_no)
        relation.save()
        page.myapps.add(relation)
        page.save()
    return HttpResponse("<script type=\"text/javascript\">window.parent.top.location.href = \"/page/" + str(page.orderNo) +  "\"</script>") 

@login_required   
def addPage(request):
    error = None
    if 'name' in request.POST:
        if len(request.POST['name']) <= 20 and len(request.POST['name']) >= 1:
            netid = request.user.username
            try:
                account = Account.objects.get(netid=netid)
            except Account.DoesNotExist:
                raise Http404
            orderNo = len(account.pages.all())
            page = Page(name=request.POST['name'], orderNo=orderNo)
            page.save()
            account.pages.add(page)
            account.save()
            #return HttpReponse("<script>alert("")</script>")
            return render_to_response('my/switchModal.html')
            #return HttpResponse("<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js\"></script><script type=\"text/javascript\">$(document).ready(function(){ $(\"a.ui-dialog-titlebar-close\", window.parent.document).trigger('click'); });</script>")
        else:
            error = "Name must be between 1 and 20 characters in length"
    return render_to_response('my/addPage.html', {'error': error})
 
@login_required   
def loading(request):
    return render_to_response('my/loading.html')
