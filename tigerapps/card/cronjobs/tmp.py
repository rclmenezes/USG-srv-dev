# endmonth.py
# Runs at midnight on the first of every month. Emails clubs with information about their members and reminders about where the archives are. Stores the archives and wipes the rest of the database.

########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from django.core.mail import send_mail, EmailMultiAlternatives
from card.models import *
from smtplib import SMTPException
from django.template.loader import render_to_string
#from email.mime.text import MIMEText
from django.utils.html import strip_tags
#from xlrd import * #reading from excel
from xlwt import * #writing to excel
from datetime import *

#date stuff
#month = date.today().month-1
#hack! check this.
#if (month == 12):
#    year = date.today().year-1
#else:
#    year = date.today().year

month = 3
year = 2012

#email to send if hardcoded
EMAIL = '[christopherrmerrick@gmail.com]'
#absolute path to place to folder in which to put archives
ARPATH = '/srv/tigerapps/card/cronjobs/archive/'

def main():
    
    print '------------------------------'
    print 'Running cronjob: endmonth.py'
    print datetime.now()
    print ''
    print 'Calling create_archive ( %s )'%ARPATH

    create_archive(ARPATH)
    
    print 'return from create_archive'
    print ''
    print 'Calling email_clubs ( %s )'% (ARPATH,)
    
    #email_clubs(ARPATH)

    print 'return from email_clubs'
    print ''
    print 'Calling empty_tables()'

    #empty_tables()

    print 'return from empty_tables'
    print ''
    print 'Done'
    print '------------------------------'
    print ''

#todo: formatting for spreadsheet (eg bold top row, autosizing columns)
#todo: add another sheet for all exchanges involving the club

def create_archive(ARPATH):

    ezxf = easyxf
    toprow = ezxf('font: bold on')

    clubs = Club.objects.all()
    for club in clubs:
        print 'Processing: %s'%club.name
        print '  creating spreadsheet'
        workbook = Workbook()
        sheet = workbook.add_sheet('Meals Out')
        #meals members had at other clubs without reciprocating
        mealsout = Exchange.objects.filter(meal_1__guest__club=club)
        #column setup
        print '  layout spreadsheet'
        for col in range(0,6):
            sheet.col(col).width = 5000
        sheet.write(r=0,c=0,label="Meal 1 Date", style=toprow)
        sheet.write(r=0,c=1,label=club.name+" Member", style=toprow)
        sheet.write(r=0,c=2,label="Host", style=toprow)
        sheet.write(r=0,c=3,label="Host Club", style=toprow)
        sheet.write(r=0,c=4,label="Meal Type", style=toprow)
        sheet.write(r=0,c=5,label="Completed?", style=toprow)

        #add data
        print '  adding data'
        currow = 1
        for ex in mealsout:
            date = ex.meal_1.date
            strdate = str(date.month)+'/'+str(date.day)+'/'+str(date.year)
            sheet.write(r=currow,c=0,label=strdate)
            sheet.write(r=currow,c=1,label=ex.meal_1.guest.full_name)
            sheet.write(r=currow,c=2,label=ex.meal_1.host.full_name)
            sheet.write(r=currow,c=3,label=ex.meal_1.host.club.name)
            sheet.write(r=currow,c=4,label=ex.meal_1.meal_type)
            if ex.meal_2:
                sheet.write(r=currow,c=5,label="yes")
            else:
                sheet.write(r=currow,c=5,label="no")
            currow = currow + 1

        #guests hosted at this club without reciprocating
        mealsin = Exchange.objects.filter(meal_1__host__club=club)
        sheet = workbook.add_sheet('Meals In ' + club.name)

        #column setup
        print '  layout spreadsheet'
        for col in range(0,6):
            sheet.col(col).width = 5000
        sheet.write(r=0,c=0,label="Meal 1 Date", style=toprow)
        sheet.write(r=0,c=1,label=club.name+" Member", style=toprow)
        sheet.write(r=0,c=2,label="Guest", style=toprow)
        sheet.write(r=0,c=3,label="Guest Club", style=toprow)
        sheet.write(r=0,c=4,label="Meal Type", style=toprow)
        sheet.write(r=0,c=5,label="Completed?", style=toprow)

        #add data
        print '  adding data'
        currow = 1
        for ex in mealsin:
            try:
                date = ex.meal_1.date
                strdate = str(date.month)+'/'+str(date.day)+'/'+str(date.year)
                sheet.write(r=currow,c=0,label=strdate)
                sheet.write(r=currow,c=1,label=ex.meal_1.host.full_name)
                sheet.write(r=currow,c=2,label=ex.meal_1.guest.full_name)
                sheet.write(r=currow,c=3,label=ex.meal_1.guest.club.name)
                sheet.write(r=currow,c=4,label=ex.meal_1.meal_type)
                if ex.meal_2:
                    sheet.write(r=currow,c=5,label="yes")
                else:
                    sheet.write(r=currow,c=5,label="no")
            except:
                sheet.write(r=currow,c=3,label='EXCEPTION')
                print 'Exception: %s, %s, %s', ex.meal_1.host, ex.meal_1.guest, ex.meal_1.date
            currow = currow + 1

        print '  closing spreadsheet'
        archivename = ARPATH+club.name + ':'+ str(month)+'-'+str(year)+'.xls'
        workbook.save(archivename)
                
    #sheet.write(r=0, c=0, label="Betina wuz here")
    #workbook.save('new.xls')
    #book = open_workbook(filename='new.xls')
    #sheet = book.sheet_by_index(0)
    #print sheet.cell_value(0, 0)

def email_clubs(EMAIL, ARPATH):
    clubs = Club.objects.all()
    for club in clubs:
        print 'Processing: %s'%club.name
        #meals members had at other clubs without reciprocating
        mealsout = Exchange.objects.filter(meal_2=None).filter(meal_1__guest__club=club)
        #guests hosted at this club without reciprocating
        mealsin = Exchange.objects.filter(meal_2=None).filter(meal_1__host__club=club)
        email = club.account.email

        print '  rendering email msg'
        html_msg = render_to_string('manager_email.html', {'club':
                                                               club.name, 'mealsout':mealsout, 'mealsin':mealsin})
        text_msg = strip_tags(html_msg)

        msg = EmailMultiAlternatives('MealChecker: End of Month Update!', 
                                     text_msg, 'MealChecker@usg.princeton.edu', [email])
        msg.attach_alternative(html_msg, "text/html")

        print '  attaching spreadsheet'
        archivename = ARPATH+club.name + ':'+ str(month)+'-'+str(year)+'.xls'
        if mealsout or mealsin:
            msg.attach_file(archivename)
        try:
            print '  sending email'
            msg.send()
        except:
            print '  ERROR: unable to send email for %s'%club.name

#very simple: clear meals
def empty_tables():
    meals = Meal.objects.all()
    for meal in meals:
        #print meal.host #debugging
        meal.delete()

if __name__ == '__main__':
    main()
