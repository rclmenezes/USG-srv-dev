from django.db import models
from stdimage import StdImageField
from django.http import Http404

MYAPP_CATEGORIES = (
    (u'Ga', u'Games/Fun'),
    (u'Pu', u'Publications and News'),
    (u'Mi', u'Miscellaneous'),
    (u'Us', u'USG/Tigerapps')
)

class MyApp(models.Model):
    myappID = models.AutoField(primary_key=True)
    name = models.CharField("Name", max_length=50)
    description = models.TextField("Description", blank=True, null=True)
    settings = models.BooleanField("Is settings", default=False)
    MYAPP_TYPES = (
        (u'R', u'Redirect'),
        (u'V', u'View'),
        (u'A', u'App'),
        (u'T', u'Test')
    )
    myappType = models.CharField(max_length=1, choices=MYAPP_TYPES)
    category = models.CharField(max_length=2, choices=MYAPP_CATEGORIES)
    MYAPP_PREFERENCES = (
        (u'M', u'Middle'),
        (u'S', u'Side'),
        (u'N', u'None')
    )
    preference = models.CharField(max_length=1, choices=MYAPP_PREFERENCES)
    height = models.IntegerField("Height of iFrame", default=300)
    scrolling = models.BooleanField("Is scrolling")
    sHeight = models.IntegerField("Side Height")
    mHeight = models.IntegerField("Middle Height")
    viewName = models.CharField("App/View Name", max_length=50, null=True, blank=True)
    link = models.CharField("Link", max_length=70, null=True, blank=True)
    posted = models.DateTimeField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'my'
        
class Page(models.Model):
    pageID = models.AutoField(primary_key=True)
    name = models.CharField("Name", max_length=20)
    myapps = models.ManyToManyField('MyAppRelation', null=True, blank=True)
    orderNo = models.IntegerField('Order')
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        app_label = 'my'
        
    def getMyApps(self):
        colList = []
        class Column:
            def __init__(self, location, relations):
                self.location = location
                self.relations = relations
        colList.append(Column('L', self.myapps.filter(column='L').order_by('sort_no')))
        colList.append(Column('M', self.myapps.filter(column='M').order_by('sort_no')))
        colList.append(Column('R', self.myapps.filter(column='R').order_by('sort_no')))
        return colList
    
class Account(models.Model):
    accountID = models.AutoField(primary_key=True)
    netid = models.CharField("NetID", max_length=8)
    pages = models.ManyToManyField(Page, null=True, blank=True)
    
    class Meta:
        app_label = 'my'
    
    def create(self):
        try:
            usgAccount = Account.objects.get(netid='usg')
            for defaultPage in usgAccount.pages.all():
                page = Page(name=defaultPage.name, orderNo=defaultPage.orderNo)
                page.save()
                for defaultRelation in defaultPage.myapps.all():
                    relation = defaultRelation
                    relation.pk = None
                    relation.save()
                    page.myapps.add(relation)
                self.pages.add(page)
        except Account.DoesNotExist:
            page = Page(name="Home", orderNo=0)
            page.save() 
            try:
                defaultPage = Page.objects.get(pageID=1)
                for defaultRelation in defaultPage.myapps.all():
                    relation = defaultRelation
                    relation.pk = None
                    relation.save()
                    page.myapps.add(relation)
                page.save()
            except Page.DoesNotExist:
                pass
            self.pages.add(page)
        self.save()
      
    # Hack-y way to get overlapping tabs  
    def getPageBar(self, page):
        pages = self.pages
        pageBar = ""
        high = 1
        hit = False
        for p in pages.all().order_by('orderNo'):
            if p == page:
                pageBar += '<div id="page_it" style="z-index: 4;">'
                if len(self.pages.all()) > 1:
                    pageBar +='<img style="visibility: hidden;" class="page_remove" width="10" height="10" src="/media/my/images/SmallX.gif"/>'
                pageBar += '<span id="tabName">' + p.name + '</span></div>'
                hit = True
                high = 3
            else:
                pageCode = '<div class="page_not" style="z-index: '+ str(high) + '; margin-'
                if not hit:
                    pageCode += 'right'
                    high += 1
                else:
                    pageCode += 'left'
                    high -= 1 
                pageCode += ': -4px;">'
                pageBar += pageCode + '<a href="/page/' + str(p.orderNo) + '/">' + p.name + '</a></div>'
        if len(pages.all()) < 4:
            pageBar += '<div id="page_plus"><a href="#">+</a></div>'
        
        return pageBar
    
    def __unicode__(self):
        return self.netid
        
class MyAppRelation(models.Model):
    relationID = models.AutoField(primary_key=True)
    myapp = models.ForeignKey(MyApp)
    COLUMN_CHOICES = (
        (u'L', u'Left'),
        (u'R', u'Right'),
        (u'M', u'Middle')
    )
    column = models.CharField(max_length=1, choices=COLUMN_CHOICES)
    sort_no = models.IntegerField("Sort Number")
    collapsed = models.BooleanField("Collapsed")
    settings = models.ManyToManyField('Setting', null=True, blank=True)
    
    class Meta:
        app_label = 'my'
    
class Setting(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    value = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'my'
    
class PageCache(models.Model):
    posted = models.DateTimeField()
    url = models.URLField()
    contents = models.TextField()
    
    class Meta:
        app_label = 'my'