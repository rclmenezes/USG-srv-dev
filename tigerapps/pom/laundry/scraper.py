'''
Created on Apr 26, 2012

@author: Nader
'''
import pom.laundry.room
import io

LAUNDRY_ROOMS = {
    '1903_HALL': '307342',
    '1915_HALL': '307342',
    '2_DICKENSON_ST.': '307342',
    'BLAIR_HALL': '30734',
    'BLOOMBERG_041': '307342',
    'BLOOMBERG_269': '307344',
    'BLOOMBERG_332': '307344',
    'BLOOMBERG_460': '307344',
    'BROWN': '307347',
    'BUTLER_-_BUILDING_A_ROOM_005': '307346',
    'BUTLER_-_BUILDING_D_ROOM_032': '307346',
    'BUYERS_HALL': '307344',
    'CLAPP_-_1927_HALL': '30734',
    'DOD_HALL': '30734',
    'EDWARDS_HALL': '30734',
    'FEINBERG_HALL': '30734',
    'FORBES_-_MAIN_INN': '30734',
    'FORBES_ANNEX': '30734',
    'HAMILTON_HALL': '307344',
    'HENRY_HALL': '307341',
    'HOLDER_HALL': '30734',
    'JOLINE_HALL': '307341',
    'LAUGHLIN_HALL': '307341',
    'LITTLE_HALL_A49': '307342',
    'LITTLE_HALL_B6': '307346',
    'LITTLE_HALL_BASEMENT_LEVEL_A5': '307341',
    'LOCKHART_HALL': '307342',
    'PATTON_HALL_4TH_FLOOR': '307341',
    'PATTON_HALL_BASEMENT_LEVEL': '307341',
    'PYNE_HALL': '307341',
    'SCULLY_HALL_-_NORTH_WING_-_2ND_FLOOR': '307341',
    'SCULLY_HALL_-_SOUTH_WING_-_1ST_FLOOR': '307341',
    'SCULLY_HALL_-_SOUTH_WING_-_4TH_FLOOR': '307342',
    'SPELMAN_HALL': '307342',
    'WHITMAN_A_119': '307346',
    'WHITMAN_C_205': '307346',
    'WHITMAN_C_305': '307346',
    'WHITMAN_C_407': '307346',
    'WHITMAN_F312': '307347',
    'WHITMAN_F403': '307347',
    'WHITMAN_FB11': '307346',
    'WHITMAN_S201': '307347',
    'WHITMAN_S301': '307347',
    'WHITMAN_S401': '307347',
    'WITHERSPOON_HALL': '307342',
}

#url_str is the base url to get the laundry data for the rooms. url_str+roomid gives
#the data for a specific room with id = roomid
url_str = 'http://classic.laundryview.com/laundry_room.php?view=c&lr='

def scrape_all():
    #dict will contain a mapping of name: room_struct pairs. room_struct.washers() returns
    #a list of [number washers free, total number of washers] and room_struct.dryers() returns a list of
    #[number of dryers free, total number of dryers].
    laundry_info = {}
    
    '''Cannot access this from dev server-- substituted with "fake" values for demo'''
    #for name,roomid in LAUNDRY_ROOMS.iteritems():
    #    laundry_info[name] = room.Room(url_str + roomid)
    return laundry_info

def print_laundry_info(laundry_info):
    '''print the results as an example'''
    for name,info in laundry_info.iteritems():
        print(name + ' \n\twashers: ' + str(info.washers()[0]) + ' free of ' + str(info.washers()[1]) + ' \n\tdryers: ' + str(info.dryers()[0]) + ' free of ' + str(info.dryers()[1]))







