from django.core.management.base import BaseCommand, CommandError
from tigerapps.rooms.views import check_undergraduate
from tigerapps.rooms.models import *

from os import environ
import sys, string, re, datetime, time
from MySQLdb import connect
from MySQLdb import cursors

class Command(BaseCommand):
    args = '<no args right now>'
    help = 'Transfers reviews from the old rooms database to the new one'

    def handle(self, *args, **options):
        self.main()
        
    def main(self):

        HOST = 'localhost'
        PORT = 3306
        tigerapps_db = 'tigerapps'
        junk_db = 'junk'
        USER = 'root'
        PASSWORD = '/tigris.panthera,.,'
        
        # Override the host if DB_SERVER_HOST is set.
        host = HOST
        if 'DB_SERVER_HOST' in environ:
            host = environ['DB_SERVER_HOST']
        
        taConn = connect(host = host, user = USER,
            passwd = PASSWORD, db = tigerapps_db)
        
        #this is named junk because the database holding the old data is named junk
        junkConn = connect(host = host, user = USER, passwd = PASSWORD, db = junk_db)
        
        # Create cursor as a dictionary:
        taCursor = taConn.cursor(cursors.DictCursor)
        reviewCursor = junkConn.cursor(cursors.DictCursor)
        
        reviewCursor.execute('select * from review')
        taCursor.execute('select * from rooms_room')
        count = 1
        review = reviewCursor.fetchone()
        
                
        while review:
            print 'checking review #%d' % count
            oldRoomCursor = junkConn.cursor(cursors.DictCursor)
            oldRoomCursor.execute('select * from room where ID = %s' % review['RoomID'])
            
            
            room = oldRoomCursor.fetchone()
            print 'checking for room with old database id = %s' % review['RoomID']
            if room == None:
                print 'could not find room with old database id = %s' % review['RoomID']
                oldRoomCursor.close()
            else:
                   
                oldBuildingCursor = junkConn.cursor(cursors.DictCursor)
                oldBuildingCursor.execute('select Name from building where ID = \'%s\'' % room['BuildingID'])
                
                oldBuildName = oldBuildingCursor.fetchone()
                
                if oldBuildName == None:
                    print ' could not find building with old database id = %s' % room['BuildingID']
                else:
                
                    newBuildingCursor = taConn.cursor(cursors.DictCursor)
                    newBuildingCursor.execute('select * from rooms_building where name = \'%s\'' % oldBuildName['Name'])
                    
                    newBuildID = newBuildingCursor.fetchone()
                    
                    try:
                        user = check_undergraduate(review['User'])
                    except:
                        try:
                            user = User.objects.get(netid='old_user')
                        except:
                            print 'the old_user user does not exist'
                            exit()
                            
                    if user == None:
                        try:
                            user = User.objects.get(netid='old_user')
                        except:
                            print 'the old_user user does not exist'
                            exit()
                            
                    try:
                        build = Building.objects.get(name=newBuildID['name'])
                    except:
                        print 'couldn\'t find building with name %s' % newBuildID['name']
                        review = reviewCursor.fetchone()
                        count = count + 1
                        continue
                        
                    try:
                        curRoom = Room.objects.get(number=room['NumberOld'], building=build)
                    except:
                        print 'couldn\'t find room %s in building %s' % (room['NumberOld'], build)
                        review = reviewCursor.fetchone()
                        count = count + 1
                        continue
                        
                    revDate = datetime.date(year=review['Date'].year, month=review['Date'].month, day=review['Date'].day)
                    try:
                        alreadyImported = Review.objects.get(room=room, summary=review['Title'], date=revDate, content=review['Text'], rating=review['Rating'], user=user)
                        print 'review already exists'
                    except:
                       titDec = review['Title'].decode('ascii', 'ignore')
                       textDec = review['Text'].decode('ascii', 'ignore')
                       curReview = Review(room=curRoom, summary=titDec.encode('latin-1'), date=revDate, content=textDec.encode('latin-1'), rating=review['Rating'], user=user)
                       curReview.save()
                       print 'going to put Review of room %s in building %s into new database for room %s in building %s' % (room['NumberOld'], oldBuildName['Name'], curRoom, build)
                    #if room['NumberOld'] != curRoom.number or oldBuildName['Name'] != build:
                        #print ' you done messed up here for room %s in building %s putting into room %s in building %s' % (room['NumberOld'], oldBuildName['Name'], curRoom.number, build)
                        
                    #sys.stderr.write("'%s'" % room['NumberOld'])
                    #sys.stderr.write("'%s'" % oldBuildName['Name'])
                    #sys.stderr.write("'%s'" % curRoom.number)
                    #sys.stderr.write("'%s'" % build)
                    
                oldRoomCursor.close()
                
                oldBuildingCursor.close()
                newBuildingCursor.close()        
                
            #time.sleep(.1)
            review = reviewCursor.fetchone()
            count = count + 1
            
            
    
        reviewCursor.close()
        taCursor.close()
        
        taConn.close()
        junkConn.close()
