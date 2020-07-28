import heroprotocol, sys, pprint, json, mpyq
from heroprotocol.versions import build, latest
from flask import Flask, render_template, Response, request
#import tkinter, tkinter.filedialog


app = Flask(__name__)

talent_sort = ['80', '20', '0g', '04', '01']
talent_tier = [0, 1, 4, 7, 10, 13, 16, 20]
global chatHistory, teamBlue, teamRed, player
player = list(dict() for i in range(0, 10))
version = '80333'
Language = 'enus'
with open('./json/herodata_{}_{}.json'.format(version, Language), encoding='utf-8') as json_file:
    herodata = json.load(json_file)


def looptime(t):
    return (t - 610) / 16

def open_replay(replay_file):
    for i in player:
        i['RegenGlobesTime'] = list()
        i['Pings'] = list()
        i['Spray'] = list()
        i['VoiceLine'] = list()
        i['PlayerKill'] = list()
        i['Death'] = list()
        i['talent'] = "https://min.hyeok.org/SILVER/#/"
    chatHistory = list()
    teamBlue = dict()
    teamRed = dict()
    teamBlue['LevelUp'] = list(0 for i in range(0, 2))
    teamRed['LevelUp'] = list(0 for i in range(0, 2))
    teamBlue['CampCapture'] = list()
    teamRed['CampCapture'] = list()


    
    #filename = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("replay files","*.StormReplay"),("all files","*.*")))
    #just disabling choosing file while in the making
    #filename = "C:/Users/smh21/Desktop/silvercity/2020-06-26 18.03.00 브락시스 전초기지.StormReplay"
    archive = mpyq.MPQArchive(replay_file)
    # Read the protocol header, this can be read with any protocol
    header = latest().decode_replay_header(archive.header['user_data_header']['content'])
    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = __import__('heroprotocol.versions.protocol%s' % baseBuild, fromlist=['baseBuild'])
    except:
        print >> sys.stderr, 'Unsupported base build: %d' % baseBuild
        sys.exit(1)

    details = protocol.decode_replay_details(archive.read_file('replay.details'))
    gameevents = archive.read_file('replay.game.events')
    messageevents = archive.read_file('replay.message.events')
    attributeevents = protocol.decode_replay_attributes_events(archive.read_file('replay.attributes.events'))
    
    if hasattr(protocol, 'decode_replay_tracker_events'):
        contents =archive.read_file('replay.tracker.events')

        for event in protocol.decode_replay_tracker_events(contents):
            if event['_event'] == 'NNet.Replay.Tracker.SScoreResultEvent':
                endOfGame = dict()
                for i in event['m_instanceList']:
                    values = list()
                    print(i['m_name'].decode())
                    for j in i['m_values'][0:10]:
                        values.append(j[0]['m_value'])
                    #if values != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
                    endOfGame[i['m_name'].decode()] = values
                pprint.pprint(endOfGame)
                
                
                            
                        



            if 'm_eventName' in event:
                #TimeSpentDead
                if event['m_eventName'].decode() == 'EndOfGameTimeSpentDead':
                    time_spent_dead = event['m_fixedData'][0]['m_value'] / 4096
                    player_number = event['m_intData'][0]['m_value'] - 1
                    player[player_number]['TimeSpentDead'] = time_spent_dead
                
                #Camp Capture
                if event['m_eventName'].decode() == 'JungleCampCapture':
                    time = looptime(event['_gameloop'])
                    if event['m_fixedData'][0]['m_value'] == 4096:
                        teamBlue['CampCapture'].append((time, event['m_stringData'][0]['m_value']))
                    elif event['m_fixedData'][0]['m_value'] == 8192:
                        teamRed['CampCapture'].append((time, event['m_stringData'][0]['m_value']))
                    

                #LevelUp
                if event['m_eventName'].decode() == 'LevelUp':
                    time = looptime(event['_gameloop'])
                    if time > 0:
                        player_number = event['m_intData'][0]['m_value'] - 1
                        if player_number < 5:
                            if time != teamBlue['LevelUp'][-1]:
                                teamBlue['LevelUp'].append(time)
                        elif player_number <= 5:
                            if time != teamRed['LevelUp'][-1]:
                                teamRed['LevelUp'].append(time)
                                
                #Talents, Hero
                if event['m_eventName'].decode() == 'EndOfGameTalentChoices':
                    player_number = event['m_intData'][0]['m_value'] - 1
                    j = 1
                    for i in event['m_stringData']:
                        if i['m_key'].decode() == 'Hero':
                            for Hero in herodata:
                                if herodata[Hero]["unitId"] == i['m_value'].decode():
                                    thisHero = Hero
                                    thisHeroName = herodata[Hero]["name"]
                                    break
                            player[player_number][i['m_key'].decode()] = thisHero
                            player[player_number]['heroName'] = thisHeroName
                            player[player_number]['talent'] += player[player_number]['Hero'] + "/"

                        elif i['m_key'].decode() != 'Win/Loss' and i['m_key'] != 'Map':
                            for which_talent in herodata[player[player_number]['Hero']]["talents"]["level{}".format(talent_tier[j])]:
                                if which_talent["nameId"] == i['m_value'].decode():
                                    player[player_number]['talent'] += talent_sort[which_talent['sort'] - 1]
                                    j += 1
                                    continue
            
                            
                #Player Kills
                
                if event['m_eventName'].decode() == 'PlayerDeath':
                    time = looptime(event['_gameloop'])
                    dead_player_number = event['m_intData'][0]['m_value'] - 1
                    player[dead_player_number]['Death'].append(time)
                    for i in range(1, len(event['m_intData'])):
                        player_number = event['m_intData'][i]['m_value'] - 1
                        player[player_number]['PlayerKill'].append((time, dead_player_number))
                
                #Spray
                if event['m_eventName'].decode() == 'LootSprayUsed':
                    time = looptime(event['_gameloop'])
                    player_number = event['m_intData'][0]['m_value'] - 1
                    player[player_number]['Spray'].append(time)

                #VoiceLine
                if event['m_eventName'].decode() == 'LootVoiceLineUsed':
                    time = looptime(event['_gameloop'])
                    player_number = event['m_intData'][0]['m_value'] - 1
                    player[player_number]['VoiceLine'].append(time)

                #Regen Globe Pickup
                if event['m_eventName'].decode() == 'RegenGlobePickedUp':
                    time = looptime(event['_gameloop'])
                    player_number = event['m_intData'][0]['m_value'] - 1
                    player[player_number]['RegenGlobesTime'].append(time)
                    
                

            #try:
                #pprint.pprint(event['m_eventName'], sys.stdout)
            #except:
                #a=1
        # Hero name, Player name, Team

    player_number = 0
    for i in details['m_playerList']:
        team = 'other'
        if i['m_teamId'] == 1:
            team = 'Red'
        if i['m_teamId'] == 0:
            team = 'Blue'
        player[player_number]['team'] = team
        player[player_number]['playerName'] = i['m_name']
        player_number += 1

    for i in protocol.decode_replay_message_events(messageevents):  
        if i['_event'] == 'NNet.Game.SChatMessage':
            time = looptime(i['_gameloop'])
            player_number = i['_userid']['m_userId']
            words = i['m_string']
            chatHistory.append((time, player_number, words)) 
        if i ['_event'] == 'NNet.Game.SPingMessage':
            player_number = i['_userid']['m_userId'] - 1
            time = looptime(i['_gameloop'])
            player[player_number]['Pings'].append(time)
    #for i in chatHistory:
        #print('({}:{}){}: {}'.format(format(int(i[0]//60), '02d'), format(int(i[0]%60), '02d'), player[int(i[1])]['playerName'].decode(), i[2].decode()))
    return [chatHistory, player, teamBlue, teamRed]

@app.route('/')
def home():

    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        replay = request.files['file']
        
        [global_chatHistory, global_player, global_teamBlue, global_teamRed] = open_replay(replay)
        
        chatlog = ""
        talents = ""
        #pprint.pprint(player)
        for i in global_player:
            talents += "{}{} ({}) : {}".format("\n", i['playerName'].decode(), i['heroName'], i['talent'])
        for i in global_chatHistory:
            chatlog += "{}({}:{}){}: {}".format("\n", format(int(i[0]//60), '02d'), format( int(i[0]%60), '02d'), player[int(i[1])]['playerName'].decode(), i[2].decode()) 
        return render_template('upload.html', chatlog=chatlog, talents=talents)
    
    else:
        return render_template('error.html')
    