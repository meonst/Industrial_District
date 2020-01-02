# -*- coding: cp949 -*-

import sys
import pprint
from heroprotocol import protocol29406
import json
import Tkinter, Tkconstants, tkFileDialog
import tkMessageBox
from Tkinter import *
from mpyq import mpyq
import pprint
from PIL import Image, ImageTk

talent_tier = [0, 1, 4, 7, 10, 13, 16, 20]
Language = 'enus'
version = '77692'
with open('./json/announcerdata_{}_{}.json'.format(version, Language)) as json_file:
    announcer = json.load(json_file)
    
with open('./json/bannerdata_{}_{}.json'.format(version, Language)) as json_file:
    banner = json.load(json_file)

with open('./json/herodata_{}_{}.json'.format(version, Language)) as json_file:
    herodata = json.load(json_file)
    
with open('./json/heroskindata_{}_{}.json'.format(version, Language)) as json_file:
    heroskin = json.load(json_file)
    
with open('./json/mountdata_{}_{}.json'.format(version, Language)) as json_file:
    mount = json.load(json_file)
    
with open('./json/portraitdata_{}_{}.json'.format(version, Language)) as json_file:
    portrait = json.load(json_file)
    
with open('./json/spraydata_{}_{}.json'.format(version, Language)) as json_file:
    spray = json.load(json_file)
    
with open('./json/voicelinedata_{}_{}.json'.format(version, Language)) as json_file:
    voiceline = json.load(json_file)





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

def resize_image(image, wanted_size):
    width_ratio = image.size[0]/wanted_size[0]
    height_ratio = image.size[1]/wanted_size[1]
    ratio = max(width_ratio, height_ratio)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image


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


plane = Tkinter.Tk()
plane.title("Silver City")
plane.geometry("1000x500")

page = Frame(plane)


#Opening Replay
def openreplay():
    plane.filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("replay files","*.StormReplay"),("all files","*.*")))
    archive = mpyq.MPQArchive(plane.filename)
    header = protocol29406.decode_replay_header(archive.header['user_data_header']['content'])
    # The header's baseBuild determines which protocol to use
    sys.path.append('./heroprotocol')
    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = __import__('protocol%s' % baseBuild)
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
            #pprint.pprint(event, sys.stdout)
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
                                
                #Talents, Hero
                if event['m_eventName'] == 'EndOfGameTalentChoices':
                    player_number = event['m_intData'][0]['m_value'] - 1
                    j = 1
                    for i in event['m_stringData']:
                        if i['m_key'] == 'Hero':
                            for Hero in herodata:
                                if herodata[Hero]["unitId"] == i['m_value']:
                                    thisHero = Hero
                            player[player_number][i['m_key']] = thisHero
                    
                        elif i['m_key'] != 'Win/Loss' and i['m_key'] != 'Map':
                            for which_talent in herodata[player[player_number]['Hero']]["talents"]["level{}".format(talent_tier[j])]:
                                if which_talent["nameId"] == i['m_value']:
                                    player[player_number]['tier{}'.format(j)] = which_talent
                                    j += 1
                                    continue
            
                            
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
            player_number = i['_userid']['m_userId']
            words = i['m_string']
            ChatHistory.append((time, player_number, words)) 
        if i ['_event'] == 'NNet.Game.SPingMessage':
            player_number = i['_userid']['m_userId'] - 1
            time = looptime(i['_gameloop'])
            player[player_number]['Pings'].append(time)
    #print "attributeevents", attributeevents
    #print "initdata", initdata
    #pprint.pprint(player, sys.stdout)
    #pprint.pprint(TeamBlue, sys.stdout)
    #pprint.pprint(TeamRed, sys.stdout)        
    for i in ChatHistory:
        print '(' + str(i[0]//60) + ':' + str(i[0]%60) + ')' + player[i[1]]['PlayerName'] + ':', i[2]
    overview_page()

#overview
def overview_page():
    new_page()
    global page
    page.pack()
    page.place(relx = 0, rely = 0.05, relwidth = 1, relheight = 0.95)

    player_button = list(0 for i in range(0, 10))
    for i in range(0, 10):
        if i // 5 == 0:
            team = 'blue'
        elif i // 5 == 1:
            team = 'red'
        
        player_button = Button(page, text = "{}({})".format(player[i]['PlayerName'], herodata[player[i]['Hero']]["name"]), fg = team)
        
        player_button.pack()
        player_button.place(relx = 0.5 * (i // 5), rely = 0.2 * (i % 5), relwidth = 0.5, relheight = 0.20)


#def player_profile(n):
    #n is player_number

def new_page():
    for child in page.winfo_children():
        child.destroy()
    
def hover_enter_talent_button(self):
    print 'enter'

def hover_leave_talent_button(self):
    print 'leave'


def talent_page():
    new_page()
    global page
    page.pack()
    page.place(relx = 0, rely = 0.05, relwidth = 1, relheight = 0.95)
    page_width = page.winfo_width()
    page_height =  page.winfo_height()
    talent_portrait_button_image = list(list(0 for i in range(0, 8)) for i in range(0, 10))
    talent_portrait_button = list(list(0 for i in range(0, 8)) for i in range(0, 10))
    for i in range(0, 10):
        if i // 5 == 0:
            background_color = 'blue'
        elif i // 5 == 1:
            background_color = 'red'
        talent_portrait_button_image[i][0] = Image.open("./images/heroportraits/{}".format(herodata[player[i]['Hero']]["portraits"]["leaderboard"]))
        talent_portrait_button_image[i][0] = ImageTk.PhotoImage(resize_image(talent_portrait_button_image[i][0], (0.2 * page_width, 0.1 * page_height)))
        talent_portrait_button[i][0] = Button(page, image = talent_portrait_button_image[i][0], relief = "flat", bg = background_color)
        talent_portrait_button[i][0].image = talent_portrait_button_image[i][0]
        talent_portrait_button[i][0].pack()
        talent_portrait_button[i][0].place(relx = 0.0, rely = 0.1 * i, relwidth = 0.3, relheight = 0.1)
    
        for j in range(1, 8):
            try:
                talent_portrait_button_image[i][j] = Image.open("./images/abilitytalents/{}".format(player[i]['tier{}'.format(j)]['icon']))
            except:
                talent_portrait_button_image[i][j] = Image.open("./images/abilitytalents/storm_ui_icon_monk_trait1.png")
            talent_portrait_button_image[i][j] = ImageTk.PhotoImage(resize_image(talent_portrait_button_image[i][j], (0.1 * page_width, 0.1 * page_height)))
            talent_portrait_button[i][j] = Button(page, image = talent_portrait_button_image[i][j], relief = "flat", bg = background_color)
            talent_portrait_button[i][j].grid()

            talent_portrait_button[i][j].bind("<Enter>", hover_enter_talent_button)
            talent_portrait_button[i][j].bind("<Leave>", hover_leave_talent_button)
            
            talent_portrait_button[i][j].image = talent_portrait_button_image[i][j]
            talent_portrait_button[i][j].pack()
            talent_portrait_button[i][j].place(relx = (j + 2) * 0.1, rely = 0.1 * i, relwidth = 0.1, relheight = 0.1)
def hero_page(n):
    pass
OpenReplay = Tkinter.Button(plane, text = "Open Replay", command = openreplay, bg = 'gray')
OpenReplay.pack()
OpenReplay.place(relx = 0 , rely = 0, relwidth = 0.20, relheight = 0.05)

Overview_Button = Button(plane, text = "Overview", fg = "black", command = overview_page)
Overview_Button.pack()
Overview_Button.place(relx = 0.20, rely = 0, relwidth = 0.20, relheight = 0.05)

Talent_Button = Button(plane, text = "Talents", fg = "black", command = talent_page)
Talent_Button.pack()
Talent_Button.place(relx = 0.40, rely = 0, relwidth = 0.20, relheight = 0.05)

Players_Button = Button(plane, text = "Players", fg = "black")
Players_Button.pack()
Players_Button.place(relx = 0.60, rely = 0, relwidth = 0.20, relheight = 0.05)

Options_Button = Button(plane, text = "Options", fg = "black")
Options_Button.pack()
Options_Button.place(relx = 0.80, rely = 0, relwidth = 0.20, relheight = 0.05)


plane.mainloop()




