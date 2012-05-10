'''
Created on Apr 26, 2012

@author: Nader
'''
import pom.laundry.room
import io

bldg_id_to_laundry_info = {'BLOOM' : (('Bloomberg 269', '3073440'), ('Bloomberg 332', '3073441'), ('Bloomberg 460', '3073442'), ('Bloomberg 41', '3073427')), 
                    'HARGH' : (('Whitman FB11', '3073469'), ('Whitman S201', '3073472'), ('Whitman C205', '3073466'), ('Whitman A119', '3073465'), ('Whitman C305', '3073467'), ('Whitman S301', '3073473'), ('Whitman C407', '3073468'), ('Whitman S401', '3073474'), ('Whitman F403', '3073471'), ('Whitman F312', '3073470')), 
                    'SCULL' : (('Scully South Wing - Fourth Floor', '3073420'), ('Scully South Wing - First Floor', '3073419'), ('Scully North Wing - Second Floor', '3073418')), 
                    'PATTN' : (('Patton Hall Basement Level', '3073416'), ('Patton Hall Fourth Floor', '3073416')), 
                    'PYNEH' : (('Pyne', '3073417'),), 
                    'HAMIL' : (('Hamilton', '3073443'),), 
                    'JOLIN' : (('Joline', '3073411'),), 
                    'LOCKH' : (('Lockhart', '3073428'),), 
                    'LITTL' : (('Little Hall B6', '3073464'), ('Little Hall A49', '3073426'), ('Little Hall Basement Level A5', '3073413')), 
                    'EDWAR' : (('Edwards', '307345'),), 
                    'FEINB' : (('Feinburg', '307346'),), 
                    'BLAIR' : (('Blair', '307342'), ('Buyers', '3073444')), 
                    'CLAPP' : (('Clapp - 1927', '307343'),), 
                    'DODHA' : (('Dod', '307344'),), 
                    'BROWN' : (('Brown', '3073475'),), 
                    'WITHR' : (('Witherspoon', '3073422'),), 
                    'LAUGH' : (('Laughlin Hall', '3073412'),), 
                    'C1915' : (('1915', '3073424'),), 
                    'HENHO' : (('Henry', '3073410'),), 
                    'FORBC' : (('Forbes Annex', '307348'), ('Forbes Main', '307347')), 
                    'SPELM' : (('Spelman', '3073421'),), 
                    'HOLDE' : (('Holder', '307349'),), 
                    '1903H' : (('1903', '3073423'),), 
                    '1976H' : (('1976', '3073462'),), 
                    'YOSEL' : (('Yoseloff', '3073463'),)}

#url_str is the base url to get the laundry data for the rooms. url_str+roomid gives
#the data for a specific room with id = roomid
url_str = 'http://classic.laundryview.com/laundry_room.php?view=c&lr='

def scrape_all():
    laundry_info = {'BLOOM' : (('Bloomberg 269', 2, 2, 3, 4), ('Bloomberg 332', 2, 2, 2, 4), ('Bloomberg 460', 0, 2, 1, 2), ('Bloomberg 41', 0, 2, 4, 4)), 
                    'HARGH' : (('Whitman FB11', 5, 5, 9, 10), ('Whitman S201', 2, 2, 3, 4), ('Whitman C205', 2, 2, 4, 4), ('Whitman A119', 2, 2, 4, 4), ('Whitman C305', 2, 2, 4, 4), ('Whitman S301', 0, 2, 1, 4), ('Whitman C407', 1, 1, 1, 2), ('Whitman S401', 1, 1, 1, 2), ('Whitman F403', 1, 1, 2, 2), ('Whitman F312', 2, 2, 4, 4)), 
                    'SCULL' : (('Scully South Wing - Fourth Floor', 3, 3, 4, 4), ('Scully South Wing - First Floor', 3, 3, 5, 6), ('Scully North Wing - Second Floor', 0, 4, 6, 6)), 
                    'PATTN' : (('Patton Hall Basement Level', 5, 5, 3, 7), ('Patton Hall Fourth Floor', 1, 1, 0, 1)), 
                    'PYNEH' : (('Pyne', 1, 5, 5, 8),), 
                    'HAMIL' : (('Hamilton', 2, 2, 2, 4),), 
                    'JOLIN' : (('Joline', 2, 3, 2, 4),), 
                    'LOCKH' : (('Lockhart', 2, 3, 4, 6),), 
                    'LITTL' : (('Little Hall B6', 3, 4, 7, 8), ('Little Hall A49', 3, 3, 4, 4), ('Little Hall Basement Level A5', 2, 4, 6, 8)), 
                    'EDWAR' : (('Edwards', 2, 4, 2, 4),), 
                    'FEINB' : (('Feinburg', 3, 4, 6, 6),), 
                    'BLAIR' : (('Blair', 5, 6, 9, 10), ('Buyers', 4, 4, 8, 8)), 
                    'CLAPP' : (('Clapp - 1927', 4, 4, 2, 3),), 
                    'DODHA' : (('Dod', 4, 5, 3, 5),), 
                    'BROWN' : (('Brown', 4, 6, 6, 6),), 
                    'WITHR' : (('Witherspoon', 4, 6, 6, 6),), 
                    'LAUGH' : (('Laughlin Hall', 5, 5, 6, 6),), 
                    'C1915' : (('1915', 5, 5, 2, 5),), 
                    'HENHO' : (('Henry', 6, 6, 4, 8),), 
                    'FORBC' : (('Forbes Annex', 6, 6, 6, 7), ('Forbes Main', 6, 6, 6, 8)), 
                    'SPELM' : (('Spelman', 6, 8, 7, 8),), 
                    'HOLDE' : (('Holder', 8, 8, 5, 8),), 
                    '1903H' : (('1903', 8, 8, 8, 8),), 
                    '1976H' : (('1976', 9, 9, 9, 10),), 
                    'YOSEL' : (('Yoseloff', 9, 9, 7, 10),)}
    
    '''
        Cannot access this from dev server-- substituted with temporary values for demo.
        You can literally just uncomment the code below on a server with access to the laundry website and everything will work.
    '''
    '''
    laundry_info = {}
    for id, info in bldg_id_to_laundry_info.iteritems():
        laundry = []
        for x in info:
            room_obj = room.Room(url_str + x[1])
            laundry.append((x[0], room_obj.washers()[0], room_obj.washers()[1], room_obj.dryers()[0], room_obj.dryers()[1]))
        laundry_info[id] = tuple(laundry)
    '''
    
    dict = {}
    for building,rooms in laundry_info.items():
        rooms_list = list(rooms)
        for i in  range(0, len(rooms)):
            room = list(rooms_list[i])
            if (room[1] == 0): #if no washers left
                room.append('#FF0000') #red
            else:
                room.append('#00AA00') #green
            if (room[3] == 0): #if no dryers left
                room.append('#FF0000') #red
            else:
                room.append('#00AA00') #green
            rooms_list[i] = tuple(room)
        rooms_list = tuple(rooms_list)
        dict[building] = rooms_list
        
    return dict

def print_laundry_info(laundry_info):
    '''print the results as an example'''
    for name,info in laundry_info.iteritems():
        print(name + ' \n\twashers: ' + str(info.washers()[0]) + ' free of ' + str(info.washers()[1]) + ' \n\tdryers: ' + str(info.dryers()[0]) + ' free of ' + str(info.dryers()[1]))





