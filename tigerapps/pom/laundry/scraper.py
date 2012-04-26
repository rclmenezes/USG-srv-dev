#! /usr/bin/python

'''
Created on Apr 26, 2012

@author: Nader
'''
import room
import io

if __name__ == '__main__':
    '''roomids.txt contains a mappring from room names to room ids'''
    f = open('roomids.txt', 'r')
    
    '''url_str is the base url to get the laundry data for the rooms. url_str+roomid gives
       the data for a specific room with id = roomid'''
    url_str = 'http://classic.laundryview.com/laundry_room.php?view=c&lr='
    
    '''dict will contain a mapping of name:[roomid, room_struct] pairs. room_struct.washers() returns
       a list of [number washers free, total number of washers] and room_struct.dryers() returns a list of
       [number of dryers free, total number of dryers].'''
    name_to_info = {}
    
    '''populate the dictionary'''
    for line in f:
        name, number = line.split(',')
        info = []
        info.append(number)
        info.append(room.Room(url_str + number))
        name_to_info[name] = info
        
    '''print the results as an example'''
    for name in name_to_info.keys():
        info = name_to_info[name][1]
        print(name + ' \n\twashers: ' + str(info.washers()[0]) + ' free of ' + str(info.washers()[1]) + ' \n\tdryers: ' + str(info.dryers()[0]) + ' free of ' + str(info.dryers()[1]))







