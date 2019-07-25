# -*- coding: cp949 -*-
import sys
import pprint
import protocol29406
import json
from mpyq import mpyq

player = list(dict() for i in range(0, 10))
for i in player:
    i['RegenGlobesTime'] = list()
    i['Pings'] = list()
    i['Spray'] = list()
    i['VoiceLine'] = list()
    i['PlayerKill'] = list()
    i['Death'] = list()
    
ChatHistory = list()
TeamBlue = dict()
TeamRed = dict()
TeamBlue['LevelUp'] = list(0 for i in range(0, 2))
TeamRed['LevelUp'] = list(0 for i in range(0, 2))
TeamBlue['CampCapture'] = list()
TeamRed['CampCapture'] = list()

def looptime(t):
    return (t - 610) / 16



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
        pprint.pprint(event, sys.stdout)
        '''
        if event.has_key('m_eventName'):
            pprint.pprint(event, sys.stdout)
        '''

        '''
        if event['_event'] == 'NNet.Replay.Tracker.SStatGameEvent':
            pprint.pprint(event, sys.stdout)
        '''
        
       
        
        
        if event.has_key('m_eventName'):
            #pprint.pprint(event['m_eventName'], sys.stdout)

            #TimeSpentDead
            if event['m_eventName'] == 'EndOfGameTimeSpentDead':
                time_spent_dead = event['m_fixedData'][0]['m_value'] / 4096
                player_number = event['m_intData'][0]['m_value'] - 1
                player[player_number]['TimeSpentDead'] = time_spent_dead
            
            #Camp Capture
            if event['m_eventName'] == 'JungleCampCapture':
                time = looptime(event['_gameloop'])
                if event['m_fixedData'][0]['m_value'] == 4096:
                    TeamBlue['CampCapture'].append((time, event['m_stringData'][0]['m_value']))
                elif event['m_fixedData'][0]['m_value'] == 8192:
                    TeamRed['CampCapture'].append((time, event['m_stringData'][0]['m_value']))
                
                
            #LevelUp
            if event['m_eventName'] == 'LevelUp':
                time = looptime(event['_gameloop'])
                if time > 0:
                    player_number = event['m_intData'][0]['m_value'] - 1
                    if player_number < 5:
                        if time != TeamBlue['LevelUp'][-1]:
                            TeamBlue['LevelUp'].append(time)
                    elif player_number <= 5:
                        if time != TeamRed['LevelUp'][-1]:
                            TeamRed['LevelUp'].append(time)
            #Talents
            if event['m_eventName'] == 'EndOfGameTalentChoices':
                player_number = event['m_intData'][0]['m_value'] - 1
                for i in event['m_stringData']:
                    player[player_number][i['m_key']] = i['m_value']
            #Player Kills
            if event['m_eventName'] == 'PlayerDeath':
                time = looptime(event['_gameloop'])
                dead_player_number = event['m_intData'][0]['m_value'] - 1
                player[dead_player_number]['Death'].append(time)
                for i in range(1, len(event['m_intData'])):
                    player_number = event['m_intData'][i]['m_value'] - 1
                    player[player_number]['PlayerKill'].append((time, dead_player_number))
            
            #Spray
            if event['m_eventName'] == 'LootSprayUsed':
                time = looptime(event['_gameloop'])
                player_number = event['m_intData'][0]['m_value'] - 1
                player[player_number]['Spray'].append(time)

            #VoiceLine
            if event['m_eventName'] == 'LootVoiceLineUsed':
                time = looptime(event['_gameloop'])
                player_number = event['m_intData'][0]['m_value'] - 1
                player[player_number]['VoiceLine'].append(time)

            #Regen Globe Pickup
            if event['m_eventName'] == 'RegenGlobePickedUp':
                time = looptime(event['_gameloop'])
                player_number = event['m_intData'][0]['m_value'] - 1
                player[player_number]['RegenGlobesTime'].append(time)

        

initdata = protocol.decode_replay_initdata(archive.read_file('replay.initData'))


#print "header", header


# Hero name, Player name, Team
player_number = 0

for i in details['m_playerList']:
    
    team = 'other'
    if i['m_teamId'] == 1:
        team = 'Red'
    if i['m_teamId'] == 0:
        team = 'Blue'
        
    player[player_number]['team'] = team
    player[player_number]['PlayerName'] = i['m_name']
    
    player_number += 1



#print "gameevents", gameevents


#Chatting history, Ping
for i in protocol.decode_replay_message_events(messageevents):
    
    if i['_event'] == 'NNet.Game.SChatMessage':
        
        time = looptime(i['_gameloop'])
        player_number = i['_userid']['m_userId'] - 1
        words = i['m_string']
        ChatHistory.append((time, player_number, words))
        
    if i ['_event'] == 'NNet.Game.SPingMessage':
        player_number = i['_userid']['m_userId'] - 1
        time = looptime(i['_gameloop'])
        player[player_number]['Pings'].append(time)


    

#print "attributeevents", attributeevents

#print "initdata", initdata


pprint.pprint(player, sys.stdout)
#pprint.pprint(TeamBlue, sys.stdout)
#pprint.pprint(TeamRed, sys.stdout)
        
'''        
for i in ChatHistory:
    print '(', i[0]//60, ':', i[0]%60, ')', player[i[1]]['PlayerName'], ':', i[2]
'''
