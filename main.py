import heroprotocol, sys, pprint, json, mpyq
from heroprotocol.versions import build, latest
from flask import Flask, render_template, Response, request, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

app = Flask(__name__)
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"])
)
#used for making talent links
talent_sort = ["80", "20", "0g", "04", "01"]
talent_tier = [0, 1, 4, 7, 10, 13, 16, 20]
#used for checking what mode the game was played in
game_mode_dict = {-1: "Custom", 50001: "Quick Match", 50021: "Versus AI", 50031: "Brawl", 50041: "Practice", 50051: "Unranked Draft", 50061: "Hero League", 50071: "Team League", 50101:"ARAM"}
#used for giving a ceiling for charts
chart_maximum = [0, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2500, 5000, 7500, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 225000, 250000, 275000, 300000, 350000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 2000000, 3000000, 5000000, 7000000, 10000000, 100000000, 1000000000, 10000000000, 100000000000, 1000000000000]
#used for giving reference to charts
chart_link = ["Takedowns", "Deaths", "SoloKill", "Assists", "ExperienceContribution", "Healing", "SiegeDamage", "StructureDamage", "MinionDamage", "HeroDamage", "SelfHealing", "TimeSpentDead", "TimeCCdEnemyHeroes", "DamageTaken", "TimeSilencingEnemyHeroes", "TimeStunningEnemyHeroes", "TeamfightHealingDone", "TeamfightDamageTaken", "TeamfightHeroDamage", "PhysicalDamage", "SpellDamage", "MinionKills", "RegenGlobes"]
chart_title = ["Kill Participation", "Deaths", "Kills", "Assists", "Experience Contribution", "Healing", "Siege Damage", "Structure Damage", "Minion Damage", "Hero Damage", "Self Healing", "Time Spent Dead", "Time CCing Enemy Heroes", "Damage Taken", "Time Silencing Enemy Heroes", "Time Stunning Enemy Heroes", "Teamfight Healing Done", "Teamfight Damage Taken", "Teamfight Hero Damage", "Physical Damage", "Spell Damage", "Minion Kills", "Regen Globes"]
#announcing global variables
#team_blue, team_red will be used for timeline
global team_blue, team_red, players
#players 0-4 is in team blue, 5-9 is in team red(i.e order and chaos)
players = list(dict() for i in range(0, 10))
#version will always be the base build for the most recent version
version = "83716"
#default language will be US english 
language = "enus"
#opening json file parsed from the game
with open("./json/herodata_{}_{}.json".format(version, language), encoding="utf-8") as json_file:
    hero_data = json.load(json_file)

map_structure_ID = {
    "DragonShire": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Bottom Keep", "Rightside Bottom Fort", "Rightside Middle Keep", "Rightside Middle Fort"],
    "ControlPoints": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "Volskaya": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "TowersOfDoom": ["placeholder", "Leftside Top Keep", "Leftside Middle Keep", "Leftside Bottom Keep", "Rightside Top Keep", "Rightside Middle Keep", "Rightside Bottom Keep"],
    "Warhead Junction":["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "HauntedWoods": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "Hanamura": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "Crypts": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "BlackheartsBay": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "BattlefieldOfEternity": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "CursedHollow": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "BraxisHoldout": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "Shrines": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Bottom Keep", "Rightside Bottom Fort", "Rightside Middle Keep", "Rightside Middle Fort"],
    "AlteracPass": ["placeholder", "Leftside Top Keep", "Leftside Top Fort", "Leftside Middle Keep", "Leftside Middle Fort", "Leftside Bottom Keep", "Leftside Bottom Fort", "Rightside Top Keep", "Rightside Top Fort", "Rightside Middle Keep", "Rightside Middle Fort", "Rightside Bottom Keep", "Rightside Bottom Fort"],
    "BraxisOutpost": ["placeholder", "Leftside Keep", "Leftside Fort", "Rightside Keep", "Rightside Fort"],
    "SilverCity": ["placeholder", "Leftside Keep", "Leftside Fort", "Rightside Keep", "Rightside Fort"],
    "LostCavern": ["placeholder", "Leftside Keep", "Leftside Fort", "Rightside Keep", "Rightside Fort"],
}

map_camp_ID = {
    "DragonShire": ["placeholder", "Leftside Siege Camp", "Leftside Bruiser Camp", "Rightside Siege Camp", "Rightside Bruiser Camp", "Bottom Bruiser Camp"],
    "ControlPoints": ["placeholder", "Leftside Siege Camp", "Leftside Bruiser Camp", "Rightside Bruiser Camp", "Rightside Siege Camp", "Boss Camp"],
    "Volskaya": ["placeholder", "Leftside Fortification Camp", "Rightside Fortification Camp", "Leftside Siege Camp", "Rightside Siege Camp", "Support Camp"],
    "TowersOfDoom": ["placeholder", "Leftside Siege Camp", "Rightside Siege Camp", "Top Siege Camp", "Boss Camp"],
    "Warhead Junction": ["placeholder", "Leftside Siege Camp", "Leftside Bruiser Camp", "Rightside Siege Camp", "Rightside Bruiser Camp", "Boss Camp"],
    "HauntedWoods": ["placeholder", "Leftside Middle Siege Camp", "Leftside Top Siege Camp", "Leftside Bruiser Camp", "Rightside Middle Siege Camp", "Rightside Bottom Siege Camp", "Rightside Bruiser Camp"],
    "Hanamura": ["placeholder", "Leftside Fortification Camp", "Rightside Fortification Camp", "Leftside Siege Camp", "Rightside Siege Camp", "Top Recon Camp", "Bottom Recon Camp"],
    "Crypts": ["placeholder", "Bottom Siege Camp", "Leftside Bruiser Camp", "Rightside Bruiser Camp", "Boss Camp"],
    "BlackheartsBay": ["placeholder", "Leftside Bruiser Camp", "Leftside Siege Camp", "Rightside Bruiser Camp", "Rightside Siege Camp", "Bottom Bruiser Camp", "Boss Camp", "Leftside Middle Skeletal Pirates", "Leftside Top Skeletal Pirates", "Rightside Middle Skeletal Pirates", "Rightside Top Skeletal Pirates"],
    "BattlefieldOfEternity": ["placeholder", "Top Siege Camp", "Leftside Bruiser Camp", "Bottom Siege Camp", "Rightside Bruiser Camp"],
    "CursedHollow": ["placeholder", "Leftside Siege Camp", "Rightside Bruiser Camp", "Rightside Siege Camp", "Leftside Bruiser Camp", "Leftside Boss Camp", "Rightside Boss Camp"],
    "BraxisHoldout": ["placeholder", "Leftside Siege Camp", "Leftside Bruiser Camp", "Rightside Siege Camp", "Rightside Bruiser Camp", "Boss Camp"],
    "Shrines": ["placeholder", "Leftside Siege Camp", "Leftside Bruiser Camp", "Rightside Siege Camp", "Rightside Bruiser Camp", "Bottom Siege Camp"],
    "AlteracPass": ["placeholder", "Leftside Siege Camp", "Top Boss Camp", "Rightside Siege Camp", "Bottom Boss Camp"], 
    "BraxisOutpost": ["placeholder", "Leftside Bruiser Camp", "Rightside Bruiser Camp"],
    "SilverCity": ["placeholder", "Leftside Siege Camp", "Rightside Siege Camp"],
}
#gametime will be given in integer t, after going through this function, it will represent time in seconds
def looptime(t):
    return (t - 610) / 16

#this is considered to be the main function of this code
def open_replay(replay_file):
    #every players will have its corresponding dictionary, filled with info
    #regen_globes_time, pings, spray, voiceline, death will record the time it has occurred
    #player_kill will be in the form of (time, number of victim)
    #talent will be in the form of a string, with length 14
    #talent_icon will be in the form of a list of length 7, each element representing one talent in order. default value will lead to a icon of a unselected monk level 1 talent(i.e a question mark icon)
    for i in players:
        i["regen_globes_time"] = list()
        i["pings"] = list()
        i["spray"] = list()
        i["voiceline"] = list()
        i["player_kill"] = list()
        i["death"] = list()
        i["talent"] = ""
        i["talent_icon"] = ["storm_ui_icon_monk_trait1.png"] * 7
    #team_blue_timeline, team_red_timeline will each record the time of a event happening
    #data will be given in chronological order (although there might be a few exceptions)
    #data will be given in the form of a list [gameloop, "name_of_event", reference data]
    team_blue_timeline = list()
    team_red_timeline = list()  

    chatlog = ""
    structure_deaths = list()
    
    #start by reading the header(it can be done with any protocol)
    #from the header open the corresponding version of protocol
    #reference for mpyq files https://github.com/eagleflo/mpyq. although it is not necessary in this occasion
    archive = mpyq.MPQArchive(replay_file)
    header = latest().decode_replay_header(archive.header["user_data_header"]["content"])
    baseBuild = header["m_version"]["m_baseBuild"]
    try:
        protocol = __import__("heroprotocol.versions.protocol%s" % baseBuild, fromlist=["baseBuild"])
    except:
        print >> sys.stderr, "Unsupported base build: %d" % baseBuild
        sys.exit(1)
    #each of these will be either a dictionary or a list with data in it
    details = protocol.decode_replay_details(archive.read_file("replay.details"))    
    init_data = protocol.decode_replay_initdata(archive.read_file("replay.initdata"))
    message_events = archive.read_file("replay.message.events")
    #game_events = archive.read_file("replay.game.events")
    #attribute_events = protocol.decode_replay_attributes_events(archive.read_file("replay.attributes.events"))
    
    #game_details will be a dictionary with certain details of the game
    game_details = dict()

    #the name of the map the game was played on
    game_details["map_name"] = details["m_title"].decode()

    #the version which the game was played on
    game_details["game_version"] = "{}.{}.{}.{}".format(header["m_version"]["m_major"], header["m_version"]["m_minor"], header["m_version"]["m_revision"], header["m_version"]["m_baseBuild"])
    
    #the regional time this game was played on
    game_details["game_time"] = datetime.fromtimestamp((details["m_timeUTC"] + details["m_timeLocalOffset"]) // 10000000 - 11644506000)
    
    #the length of the game
    game_details["game_length"] = "{0:02d}:{1:02d}".format(int(header["m_elapsedGameLoops"] / 16) // 60, int((header["m_elapsedGameLoops"] / 16) % 60))
    
    #the winner of the game(assuming there are no ties)
    game_details["winner"] = ["Blue", "Red"][details["m_playerList"][0]["m_result"] - 1]
    
    #the game_mode this game is played on(default set to Unknown to avoid error)
    game_details["game_mode"] = "Unknown"
    if init_data["m_syncLobbyState"]["m_gameDescription"]["m_gameOptions"]["m_ammId"] in game_mode_dict:
        game_details["game_mode"] = game_mode_dict[init_data["m_syncLobbyState"]["m_gameDescription"]["m_gameOptions"]["m_ammId"]]

    #will be going through tracker events
    if hasattr(protocol, "decode_replay_tracker_events"):
        contents = protocol.decode_replay_tracker_events(archive.read_file("replay.tracker.events"))
        for event in contents:   
            #"NNet.Replay.Tracker.SScoreResultEvent" always happens at the end. I assume these stats are normally used to determine awards
            if event["_event"] == "NNet.Replay.Tracker.SScoreResultEvent":
                statistics = dict()
                statistics_maximum = dict()
                for i in event["m_instanceList"]:
                    values = list()
                    for j in i["m_values"][0:10]:
                        values.append(j[0]["m_value"])
                    statistics[i["m_name"].decode()] = values
                    #this part is to determine the ceiling to use for charts
                    for j in range(0, 55):
                        if max(values) < chart_maximum[j]:
                            statistics_maximum[i["m_name"].decode()] = chart_maximum[j]
                            break
            #checking for notable events
            if "m_eventName" in event:
                #if event["m_eventName"].decode() not in ["LootWheelUsed", "EndOfGameUpVotesCollected","RegenGlobePickedUp","PlayerDeath","LevelUp","JungleCampCapture","TalentChosen","EndOfGameXPBreakdown","EndOfGameTimeSpentDead","EndOfGameTalentChoices", "LootVoiceLineUsed","PeriodicXPBreakdown","LootSprayUsed","TownStructureDeath","GameStart","PlayerInit","TownStructureInit","PlayerSpawned","JungleCampInit","GatesOpen"]:
                #    print(event["m_eventName"].decode())

                #Structuer Death [gameloop, broken structure, related players]
                if event["m_eventName"].decode() == "TownStructureDeath":    
                    #print("건물", int((looptime(event["_gameloop"]) + 38) // 60), int((looptime(event["_gameloop"]) + 38) % 60), event["m_intData"][0]["m_value"])
                    players_involved = list()
                    for i in event["m_intData"]:
                        if i["m_key"] == b"TownID":
                            structure_ID = i["m_value"]
                        else:
                            players_involved.append(i["m_value"] - 1)
                    structure_deaths.append([event["_gameloop"], structure_ID, players_involved])

                #Player Death [gameloop, event_name, [victim, related players]]
                if event["m_eventName"].decode() == "PlayerDeath":
                    players_involved = list()
                    for i in event["m_intData"]:
                        players_involved.append(i["m_value"] - 1)
                    if players_involved[0] < 5:
                        team_blue_timeline.append([event["_gameloop"], "player_death", players_involved])
                    if players_involved[0] > 5:
                        team_red_timeline.append([event["_gameloop"], "player_death", players_involved])

                #Camp Capture 
                if event["m_eventName"].decode() == "JungleCampCapture":
                    #print("용병캠프", int((looptime(event["_gameloop"]) + 38) // 60), int((looptime(event["_gameloop"]) + 38) % 60), event["m_intData"][0]["m_value"])
                    if event["m_fixedData"][0]["m_value"] == 4096:
                        team_blue_timeline.append([event["_gameloop"], "camp_capture", event["m_intData"][0]["m_value"]])
                    elif event["m_fixedData"][0]["m_value"] == 8192:
                        team_red_timeline.append([event["_gameloop"], "camp_capture", event["m_intData"][0]["m_value"]])

                #Level Up, will only be checking level up for user 0 and 5 since the level up time is the same for everyone else on the same team
                if event["m_eventName"].decode() == "LevelUp":
                    if event["_gameloop"] > 610:
                        player_number = event["m_intData"][0]["m_value"] - 1
                        if player_number == 0:
                            team_blue_timeline.append([event["_gameloop"], "level_up", event["m_intData"][1]["m_value"]])
                        elif player_number == 5:
                            team_red_timeline.append([event["_gameloop"], "level_up", event["m_intData"][1]["m_value"]])

                #TimeSpentDead. Since this automatically adds time at the point of death, it may not correctly represent the actual time dead.
                if event["m_eventName"].decode() == "EndOfGameTimeSpentDead":
                    time_spent_dead = event["m_fixedData"][0]["m_value"] / 4096
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["time_spent_dead"] = time_spent_dead

                #"EndOfGameTalentChoices" has multiple info inside, however only the hero names and talent choices will be used.
                #Hero 
                if event["m_eventName"].decode() == "EndOfGameTalentChoices":
                    player_number = event["m_intData"][0]["m_value"] - 1
                    j = 1
                    for i in event["m_stringData"]:
                        if i["m_key"].decode() == "Hero":
                            if i["m_value"].decode() == "HeroMedivhRaven":
                                this_hero = "Medivh"
                            if i["m_value"].decode() == "HeroDVaPilot":
                                this_hero = "DVa"
                            if i["m_value"].decode() == "HeroAlexstraszaDragon":
                                this_hero = "Alexstrasza"
                                
                            for hero in hero_data:
                                if hero_data[hero]["unitId"] == i["m_value"].decode():
                                    this_hero = hero
                                    break
                            players[player_number]["hero"] = this_hero
                            players[player_number]["hero_name"] = hero_data[this_hero]["name"]
                            players[player_number]["hero_link"] = players[player_number]["hero"]
                            players[player_number]["party_panel_portrait"] = hero_data[players[player_number]["hero_link"]]["portraits"]["partyPanel"]
                            players[player_number]["minimap_portrait"] = hero_data[players[player_number]["hero_link"]]["portraits"]["minimap"]
                        #map_link will be used to determine which map should be used for identifying camps and structures
                        elif i["m_key"].decode() == "Map":
                            map_link = i["m_value"].decode()
                        #Talents
                        elif i["m_key"].decode() != "Win/Loss":
                            for which_talent in hero_data[players[player_number]["hero"]]["talents"]["level{}".format(talent_tier[j])]:
                                
                                if which_talent["nameId"] == i["m_value"].decode():
                                    players[player_number]["talent_icon"][j - 1] = which_talent["icon"]
                                    players[player_number]["talent"] += talent_sort[which_talent["sort"] - 1]
                                    j += 1
                                    continue
                
                #Player Kills
                if event["m_eventName"].decode() == "PlayerDeath":
                    time = looptime(event["_gameloop"])
                    dead_player_number = event["m_intData"][0]["m_value"] - 1
                    players[dead_player_number]["death"].append(time)
                    for i in range(1, len(event["m_intData"])):
                        player_number = event["m_intData"][i]["m_value"] - 1
                        if player_number < 10 and player_number >= 0: #this is necessary since the player_number will be 10 or 11 when the final blow is caused by minions
                            players[player_number]["player_kill"].append((time, dead_player_number))
                
                #Spray
                if event["m_eventName"].decode() == "LootSprayUsed":
                    time = looptime(event["_gameloop"])
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["spray"].append(time)

                #VoiceLine
                if event["m_eventName"].decode() == "LootVoiceLineUsed":
                    time = looptime(event["_gameloop"])
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["voiceline"].append(time)

                #Regen Globe Pickup, this might not function properly for heroes such as TLV or Rexxar
                if event["m_eventName"].decode() == "RegenGlobePickedUp":
                    time = looptime(event["_gameloop"])
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["regen_globes_time"].append(time)
                    
    #This part is needed for the talent link to function as intended even in cases where the game ends pre 20
    for i in players:
        i["talent"] = i["talent"].ljust(14, "0")
        
    #Player name, Team
    player_number = 0
    for i in details["m_playerList"]:
        players[player_number]["team"] = ["blue", "red"][i["m_teamId"]]
        players[player_number]["player_name"] = i["m_name"].decode()
        player_number += 1
    
    for i in protocol.decode_replay_message_events(message_events):  
    #Chat Messages
        if i["_event"] == "NNet.Game.SChatMessage":
            chatlog += "{}({}:{}){}: {}".format("\n", format(int(looptime(i["_gameloop"])//60), "02d"), format( int(looptime(i["_gameloop"])%60), "02d"), players[i["_userid"]["m_userId"]]["player_name"], i["m_string"].decode()) 

    #Ping Messages
        if i ["_event"] == "NNet.Game.SPingMessage":
            player_number = i["_userid"]["m_userId"]
            time = looptime(i["_gameloop"])
            players[player_number]["pings"].append(time)

    #This will soon be changed
    stats = statistics.copy()
    exclude_from_stats = ["TeamWinsDiablo","TeamWinsFemale", "TeamWinsMale", "TeamWinsStarCraft", "TeamWinsWarcraft","WinsWarrior", "WinsAssassin", "WinsSupport","WinsSpecialist","WinsStarCraft", "WinsDiablo", "WinsWarcraft", "WinsMale", "WinsFemale", "PlaysStarCraft", "PlaysDiablo", "PlaysOverwatch", "PlaysWarCraft", "PlaysWarrior", "PlaysAssassin", "PlaysSupport", "PlaysSpecialist", "PlaysMale", "PlaysFemale", "Tier1Talent", "Tier2Talent", "Tier3Talent", "Tier4Talent", "Tier5Talent", "Tier6Talent", "Tier7Talent", "TeamLevel", "LessThan4Deaths", "LessThan3TownStructuresLost", "Level", "MetaExperience", "TeamTakedowns", "Role", "EndOfMatchAwardGivenToNonwinner", "GameScore", "LunarNewYearSuccesfulArtifactTurnIns", "LunarNewYearEventCompleted", "StarcraftDailyEventCompleted", "StarcraftPiecesCollected", "LunarNewYearRoosterEventCompleted", "PachimariMania", "TouchByBlightPlague", "EscapesPerformed", "VengeancesPerformed", "TeamfightEscapesPerformed", "OutnumberedDeaths", "EndOfMatchAwardMVPBoolean", "EndOfMatchAwardHighestKillStreakBoolean", "EndOfMatchAwardMostVengeancesPerformedBoolean", "EndOfMatchAwardMostDaredevilEscapesBoolean", "EndOfMatchAwardMostEscapesBoolean", "EndOfMatchAwardMostXPContributionBoolean", "EndOfMatchAwardMostHeroDamageDoneBoolean", "EndOfMatchAwardMostKillsBoolean", "EndOfMatchAwardHatTrickBoolean", "EndOfMatchAwardClutchHealerBoolean", "EndOfMatchAwardMostProtectionBoolean", "EndOfMatchAward0DeathsBoolean", "EndOfMatchAwardMostSiegeDamageDoneBoolean", "EndOfMatchAwardMostDamageTakenBoolean", "EndOfMatchAward0OutnumberedDeathsBoolean", "EndOfMatchAwardMostHealingBoolean", "EndOfMatchAwardMostStunsBoolean", "EndOfMatchAwardMostRootsBoolean", "EndOfMatchAwardMostSilencesBoolean", "EndOfMatchAwardMostMercCampsCapturedBoolean", "EndOfMatchAwardMostTeamfightDamageTakenBoolean", "EndOfMatchAwardMostTeamfightHealingDoneBoolean", "EndOfMatchAwardMostTeamfightHeroDamageDoneBoolean", "EndOfMatchAwardMostDamageToMinionsBoolean", "EndOfMatchAwardMapSpecificBoolean", "EndOfMatchAwardMostDragonShrinesCapturedBoolean", "EndOfMatchAwardMostTimePushingBoolean", "EndOfMatchAwardMostTimeOnPointBoolean", "EndOfMatchAwardMostInterruptedCageUnlocksBoolean", "EndOfMatchAwardMostSeedsCollectedBoolean", "EndOfMatchAwardMostDamageToPlantsBoolean", "EndOfMatchAwardMostCurseDamageDoneBoolean", "EndOfMatchAwardMostCoinsPaidBoolean", "EndOfMatchAwardMostImmortalDamageBoolean", "EndOfMatchAwardMostDamageDoneToZergBoolean", "EndOfMatchAwardMostTimeInTempleBoolean", "EndOfMatchAwardMostGemsTurnedInBoolean", "EndOfMatchAwardMostSkullsCollectedBoolean", "EndOfMatchAwardMostAltarDamageDone", "EndOfMatchAwardMostNukeDamageDoneBoolean", "KilledTreasureGoblin", "TimeOnPoint", "CageUnlocksInterrupted", "GardenSeedsCollectedByPlayer", "PlaysNexus", "PlaysOverwatchOrNexus", "Multikill", "DamageDoneToZerg"]
    for i in exclude_from_stats:
        stats.pop(i, None)
    #-------------------------
    
    #structure deaths for 3 lane maps except Towers of Doom
    if map_link in ["DragonShire", "ControlPoints", "Volskaya", "Warhead Junction", "Shrines", "AlteracPass", "HauntedWoods", "CursedHollow", "Crypts", "BlackheartsBay"]:
        for i in structure_deaths:
            if i[1] <= 6:
                team_blue_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])    
            if i[1] > 6:
                team_red_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])

    #structure deaths for 2 lane maps
    if map_link in ["BattlefieldOfEternity", "BraxisHoldout", "Hanamura"]:
        for i in structure_deaths:
            if i[1] <= 4:
                team_blue_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])    
            if i[1] > 4:
                team_red_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])

    #structure deaths for 1 lane maps except Industrial District
    if map_link in ["BraxisOutpost", "SilverCity", "LostCavern"]:
        for i in structure_deaths:
            if i[1] <= 2:
                team_blue_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])    
            if i[1] > 2:
                team_red_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])
    
    #structure deaths for Towers of Doom
    if map_link == "TowersOfDoom":
        structure_owner = ["placeholder", "blue", "blue", "blue", "red", "red", "red"]
        for i in structure_deaths:
            if structure_owner[i[1]] == "blue":
                team_blue_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])
                structure_owner[i[1]] = "red"
            elif structure_owner[i[1]] == "red":
                team_red_timeline.append([i[0], "structure_death", map_structure_ID[map_link][i[1]], i[2]])
                structure_owner[i[1]] = "blue"

    #map specific camp names
    for i in team_blue_timeline:
        if i[1] == "camp_capture":
            i[2] = map_camp_ID[map_link][i[2]]
    for i in team_red_timeline:
        if i[1] == "camp_capture":
            i[2] = map_camp_ID[map_link][i[2]]

    return [chatlog, players, stats, statistics, statistics_maximum, game_details, team_blue_timeline, team_red_timeline]



@app.route("/", methods=["GET", "POST"])
def replay_page():
    if request.method == "POST":
        replay = request.files["file"]
        return_data = open_replay(replay)
       
        replay_template = env.get_template("replay.html")
        css_URL = url_for("static", filename="replay.css")
        js_URL = url_for("static", filename="replay.js")
        return replay_template.render(css_URL=css_URL, js_URL=js_URL, chatlog=return_data[0], players=return_data[1], stats=return_data[2], statistics=return_data[3], statistics_maximum=return_data[4], game_details=return_data[5], team_blue_timeline=return_data[6], team_red_timeline=return_data[7], chart_title=chart_title, chart_link=chart_link)
        
    else:
        css_URL = url_for("static", filename="home.css")
        home_template = env.get_template("home.html")
        return home_template.render(css_URL=css_URL)

