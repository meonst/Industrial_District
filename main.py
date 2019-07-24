# -*- coding: cp949 -*-
import sys
import pprint
import protocol29406
import json
from mpyq import mpyq



class EventLogger:
    def __init__(self):
        self._event_stats = {}

    def log(self, output, event):
        # update stats
        if '_event' in event and '_bits' in event:
            stat = self._event_stats.get(event['_event'], [0, 0])
            stat[0] += 1  # count of events
            stat[1] += event['_bits']  # count of bits
            self._event_stats[event['_event']] = stat
        # write structure
        #if args.json:
        s = json.dumps(event, encoding="ISO-8859-1")
        print(s)
        #else:
        #    pass
        #pprint.pprint(event, stream=output)
    def log_stats(self, output):
        for name, stat in sorted(self._event_stats.iteritems(), key=lambda x: x[1][1]):
            print >> output, '"%s", %d, %d,' % (name, stat[0], stat[1] / 8)



logger = EventLogger()

# Read the protocol header, this can be read with any protocol
archive = mpyq.MPQArchive('2019-07-10 20.26.59 영원의 전쟁터.StormReplay')

header = protocol29406.decode_replay_header(archive.header['user_data_header']['content'])

# The header's baseBuild determines which protocol to use
baseBuild = header['m_version']['m_baseBuild']
protocol = __import__('protocol%s' % (baseBuild))
try:
    protocol = __import__('protocol%s' % (baseBuild))
except:
    print >> sys.stderr, 'Unsupported base build: %d' % baseBuild
    sys.exit(1)

    
details = protocol.decode_replay_details(archive.read_file('replay.details'))

gameevents = archive.read_file('replay.game.events')
#for event in protocol.decode_replay_game_events(contents):
    #gameevents.log(sys.stdout, event)

messageevents = archive.read_file('replay.message.events')
#for event in protocol.decode_replay_message_events(contents):
#    messageevents.log(sys.stdout, event)

attributeevents = protocol.decode_replay_attributes_events(archive.read_file('replay.attributes.events'))


if hasattr(protocol, 'decode_replay_tracker_events'):
    contents = archive.read_file('replay.tracker.events')
    
    for event in protocol.decode_replay_tracker_events(contents):
        '''
        if event.has_key('m_eventName'):
            pprint.pprint(event, sys.stdout)
        '''
        
        if event.has_key('m_eventName'):
            if event['m_eventName'] == 'EndOfGameTalentChoices':
                print event['m_intData'][0]['m_value']
                for i in event['m_stringData']:
                    print i['m_value']
                #pprint.pprint(event['m_stringData'], sys.stdout)
                
            
        '''
        if event['_event'] == 'NNet.Replay.Tracker.SStatGameEvent':
            pprint.pprint(event, sys.stdout)
        '''
            
        '''
        #Regen Globe Pickup
        if event.has_key('m_eventName'):
            if event['m_eventName'] == 'RegenGlobePickedUp':
                print event
        '''


        

initdata = protocol.decode_replay_initdata(archive.read_file('replay.initData'))


#print "header", header

'''
# Hero name, Player name, Team
print "details"
for i in details['m_playerList']:
    team = 'other'
    if i['m_teamId'] == 1:
        team = 'red'
    if i['m_teamId'] == 0:
        team = 'blue'
        
    print i['m_hero'], i['m_name'], team
''' 
    

#print "gameevents", gameevents

'''
#Chatting history, Ping
print "messageevents"
for i in protocol.decode_replay_message_events(messageevents):
    #pprint.pprint(i, stream = sys.stdout)
    
    if i['_event'] != 'NNet.Game.SLoadingProgressMessage':
        pass
    if i['_event'] == 'NNet.Game.SChatMessage':
        print i['_userid'], ":", i['m_string']
    if i ['_event'] == 'NNet.Game.SPingMessage':
        print i['_userid']
'''    

    

#print "attributeevents", attributeevents

#print "initdata", initdata



