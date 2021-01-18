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

talent_sort = ["80", "20", "0g", "04", "01"]
talent_tier = [0, 1, 4, 7, 10, 13, 16, 20]
game_mode_dict = {-1: "Custom", 50001: "Quick Match", 50021: "Versus AI", 50031: "Brawl", 50041: "Practice", 50051: "Unranked Draft", 50061: "Hero League", 50071: "Team League", 50101:"ARAM"}


chart_link = ["ExperienceContribution", "SiegeDamage", "HeroDamage", "TimeSpentDead", "DamageTaken", "TeamfightDamageTaken", "TeamfightHeroDamage", "MinionKills"]
chart_title = ["EXP Contribution", "Siege Damage", "Hero Damage", "Time Spent Dead", "Damage Taken", "Teamfight Damage Taken", "Teamfight Damage Dealt", "Minion Kills"]
chart_link_ID = ["Exp", "SiegeDmg", "HeroDmg", "DeathTime", "DmgTaken", "TeamFightDmgTaken", "TeamFightDmg", "MinionKills"]

global chat_history, team_blue, team_red, players
players = list(dict() for i in range(0, 10))
version = "83004"
language = "enus"
with open("./json/herodata_{}_{}.json".format(version, language), encoding="utf-8") as json_file:
    hero_data = json.load(json_file)



def looptime(t):
    return (t - 610) / 16

def open_replay(replay_file):
    for i in players:
        i["regen_globes_time"] = list()
        i["pings"] = list()
        i["spray"] = list()
        i["voiceline"] = list()
        i["player_kill"] = list()
        i["death"] = list()
        i["talent"] = ""
        i["talent_icon"] = ["storm_ui_icon_monk_trait1.png"] * 7
    chat_history = list()
    team_blue = dict()
    team_red = dict()
    team_blue["level_up"] = list(0 for i in range(0, 2))
    team_red["level_up"] = list(0 for i in range(0, 2))
    team_blue["camp_capture"] = list()
    team_red["camp_capture"] = list()


    
    #filename = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("replay files","*.StormReplay"),("all files","*.*")))
    #just disabling choosing file while in the making
    #filename = "C:/Users/smh21/Desktop/silvercity/2020-06-26 18.03.00 브락시스 전초기지.StormReplay"
    archive = mpyq.MPQArchive(replay_file)
    # Read the protocol header, this can be read with any protocol
    header = latest().decode_replay_header(archive.header["user_data_header"]["content"])
    baseBuild = header["m_version"]["m_baseBuild"]
    try:
        protocol = __import__("heroprotocol.versions.protocol%s" % baseBuild, fromlist=["baseBuild"])
    except:
        print >> sys.stderr, "Unsupported base build: %d" % baseBuild
        sys.exit(1)

    details = protocol.decode_replay_details(archive.read_file("replay.details"))    
    init_data = protocol.decode_replay_initdata(archive.read_file("replay.initdata"))
    game_events = archive.read_file("replay.game.events")
    message_events = archive.read_file("replay.message.events")
    attribute_events = protocol.decode_replay_attributes_events(archive.read_file("replay.attributes.events"))

    game_details = dict()
    game_details["map_name"] = details["m_title"].decode()
    game_details["game_version"] = "{}.{}.{}.{}".format(header["m_version"]["m_major"], header["m_version"]["m_minor"], header["m_version"]["m_revision"], header["m_version"]["m_baseBuild"])
    game_details["game_time"] = datetime.fromtimestamp((details["m_timeUTC"] + details["m_timeLocalOffset"]) // 10000000 - 11644506000)
    game_details["game_length"] = "{0:02d}:{1:02d}".format(int(header["m_elapsedGameLoops"] / 16) // 60, int((header["m_elapsedGameLoops"] / 16) % 60))
    game_details["game_mode"] = "Unknown"
    if init_data["m_syncLobbyState"]["m_gameDescription"]["m_gameOptions"]["m_ammId"] in game_mode_dict:
        game_details["game_mode"] = game_mode_dict[init_data["m_syncLobbyState"]["m_gameDescription"]["m_gameOptions"]["m_ammId"]]

    if hasattr(protocol, "decode_replay_tracker_events"):
        contents = archive.read_file("replay.tracker.events")

        for event in protocol.decode_replay_tracker_events(contents):
            if event["_event"] == "NNet.Replay.Tracker.SScoreResultEvent":
                statistics = dict()
                for i in event["m_instanceList"]:
                    values = list()
                    for j in i["m_values"][0:10]:
                        values.append(j[0]["m_value"])
                    if values != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
                        statistics[i["m_name"].decode()] = values




            if "m_eventName" in event:
                #TimeSpentDead
                if event["m_eventName"].decode() == "EndOfGameTimeSpentDead":
                    time_spent_dead = event["m_fixedData"][0]["m_value"] / 4096
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["time_spent_dead"] = time_spent_dead
                
                #Camp Capture
                if event["m_eventName"].decode() == "Junglecamp_capture":
                    time = looptime(event["_gameloop"])
                    if event["m_fixedData"][0]["m_value"] == 4096:
                        team_blue["camp_capture"].append((time, event["m_stringData"][0]["m_value"]))
                    elif event["m_fixedData"][0]["m_value"] == 8192:
                        team_red["camp_capture"].append((time, event["m_stringData"][0]["m_value"]))
                    

                #Level Up
                if event["m_eventName"].decode() == "LevelUp":
                    time = looptime(event["_gameloop"])
                    if time > 0:
                        player_number = event["m_intData"][0]["m_value"] - 1
                        if player_number < 5:
                            if time != team_blue["level_up"][-1]:
                                team_blue["level_up"].append(time)
                        elif player_number <= 5:
                            if time != team_red["level_up"][-1]:
                                team_red["level_up"].append(time)
                                
                #Hero
                
                
                if event["m_eventName"].decode() == "EndOfGameTalentChoices":
                    player_number = event["m_intData"][0]["m_value"] - 1
                    j = 1
                    for i in event["m_stringData"]:
                        if i["m_key"].decode() == "Hero":
                            if i["m_value"].decode() == "HeroMedivhRaven":
                                thisHero = "Medivh"
                                thisHeroName = hero_data["Medivh"]["name"]
                            if i["m_value"].decode() == "HeroDVaPilot":
                                thisHero = "DVa"
                                thisHeroName = hero_data["DVa"]["name"]
                            for Hero in hero_data:
                                if hero_data[Hero]["unitId"] == i["m_value"].decode():
                                    thisHero = Hero
                                    thisHeroName = hero_data[Hero]["name"]
                                    break
                            players[player_number][i["m_key"].decode()] = thisHero
                            players[player_number]["hero_name"] = thisHeroName
                            players[player_number]["hero_link"] = players[player_number]["Hero"]
                            players[player_number]["party_panel_portrait"] = hero_data[players[player_number]["hero_link"]]["portraits"]["partyPanel"]
                            players[player_number]["minimap_portrait"] = hero_data[players[player_number]["hero_link"]]["portraits"]["minimap"]
                            
                #Talents
                        elif i["m_key"].decode() != "Win/Loss" and i["m_key"] != "Map":
                            for which_talent in hero_data[players[player_number]["Hero"]]["talents"]["level{}".format(talent_tier[j])]:
                                
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

                #Regen Globe Pickup
                if event["m_eventName"].decode() == "RegenGlobePickedUp":
                    time = looptime(event["_gameloop"])
                    player_number = event["m_intData"][0]["m_value"] - 1
                    players[player_number]["regen_globes_time"].append(time)
                    
                


    for i in players:
        i["talent"] = i["talent"].ljust(14, "0")
    # Hero name, Player name, Team
    player_number = 0
    for i in details["m_playerList"]:
        team = "other"   
        if i["m_teamId"] == 0:
            team = "blue"
        if i["m_teamId"] == 1:
            team = "red"

        players[player_number]["team"] = team
        players[player_number]["player_name"] = i["m_name"].decode()
        player_number += 1

    for i in protocol.decode_replay_message_events(message_events):  
        if i["_event"] == "NNet.Game.SChatMessage":
            time = looptime(i["_gameloop"])
            player_number = i["_userid"]["m_userId"]
            words = i["m_string"]
            chat_history.append((time, player_number, words)) 
        if i ["_event"] == "NNet.Game.SPingMessage":
            player_number = i["_userid"]["m_userId"] - 1
            time = looptime(i["_gameloop"])
            players[player_number]["pings"].append(time)
    stats = statistics.copy()
    exclude_from_stats = ["TeamWinsDiablo","TeamWinsFemale", "TeamWinsMale", "TeamWinsStarCraft", "TeamWinsWarcraft","WinsWarrior", "WinsAssassin", "WinsSupport","WinsSpecialist","WinsStarCraft", "WinsDiablo", "WinsWarcraft", "WinsMale", "WinsFemale", "PlaysStarCraft", "PlaysDiablo", "PlaysOverwatch", "PlaysWarCraft", "PlaysWarrior", "PlaysAssassin", "PlaysSupport", "PlaysSpecialist", "PlaysMale", "PlaysFemale", "Tier1Talent", "Tier2Talent", "Tier3Talent", "Tier4Talent", "Tier5Talent", "Tier6Talent", "Tier7Talent", "TeamLevel", "LessThan4Deaths", "LessThan3TownStructuresLost", "Level", "MetaExperience", "TeamTakedowns", "Role", "EndOfMatchAwardGivenToNonwinner", "GameScore", "LunarNewYearSuccesfulArtifactTurnIns", "LunarNewYearEventCompleted", "StarcraftDailyEventCompleted", "StarcraftPiecesCollected", "LunarNewYearRoosterEventCompleted", "PachimariMania", "TouchByBlightPlague", "EscapesPerformed", "VengeancesPerformed", "TeamfightEscapesPerformed", "OutnumberedDeaths", "EndOfMatchAwardMVPBoolean", "EndOfMatchAwardHighestKillStreakBoolean", "EndOfMatchAwardMostVengeancesPerformedBoolean", "EndOfMatchAwardMostDaredevilEscapesBoolean", "EndOfMatchAwardMostEscapesBoolean", "EndOfMatchAwardMostXPContributionBoolean", "EndOfMatchAwardMostHeroDamageDoneBoolean", "EndOfMatchAwardMostKillsBoolean", "EndOfMatchAwardHatTrickBoolean", "EndOfMatchAwardClutchHealerBoolean", "EndOfMatchAwardMostProtectionBoolean", "EndOfMatchAward0DeathsBoolean", "EndOfMatchAwardMostSiegeDamageDoneBoolean", "EndOfMatchAwardMostDamageTakenBoolean", "EndOfMatchAward0OutnumberedDeathsBoolean", "EndOfMatchAwardMostHealingBoolean", "EndOfMatchAwardMostStunsBoolean", "EndOfMatchAwardMostRootsBoolean", "EndOfMatchAwardMostSilencesBoolean", "EndOfMatchAwardMostMercCampsCapturedBoolean", "EndOfMatchAwardMostTeamfightDamageTakenBoolean", "EndOfMatchAwardMostTeamfightHealingDoneBoolean", "EndOfMatchAwardMostTeamfightHeroDamageDoneBoolean", "EndOfMatchAwardMostDamageToMinionsBoolean", "EndOfMatchAwardMapSpecificBoolean", "EndOfMatchAwardMostDragonShrinesCapturedBoolean", "EndOfMatchAwardMostTimePushingBoolean", "EndOfMatchAwardMostTimeOnPointBoolean", "EndOfMatchAwardMostInterruptedCageUnlocksBoolean", "EndOfMatchAwardMostSeedsCollectedBoolean", "EndOfMatchAwardMostDamageToPlantsBoolean", "EndOfMatchAwardMostCurseDamageDoneBoolean", "EndOfMatchAwardMostCoinsPaidBoolean", "EndOfMatchAwardMostImmortalDamageBoolean", "EndOfMatchAwardMostDamageDoneToZergBoolean", "EndOfMatchAwardMostTimeInTempleBoolean", "EndOfMatchAwardMostGemsTurnedInBoolean", "EndOfMatchAwardMostSkullsCollectedBoolean", "EndOfMatchAwardMostAltarDamageDone", "EndOfMatchAwardMostNukeDamageDoneBoolean"]
    for i in exclude_from_stats:
        stats.pop(i, None)
    return [chat_history, players, stats, statistics, game_details]



@app.route("/", methods=["GET", "POST"])
def replay_page():
    if request.method == "POST":
        replay = request.files["file"]
        return_data = open_replay(replay)
        
        chatlog = ""
        for i in return_data[0]:
            chatlog += "{}({}:{}){}: {}".format("\n", format(int(i[0]//60), "02d"), format( int(i[0]%60), "02d"), players[int(i[1])]["player_name"], i[2].decode()) 

        replay_template = env.get_template("replay.html")
        css_URL = url_for("static", filename="replay.css")
        js_URL = url_for("static", filename="replay.js")
        return replay_template.render(css_URL=css_URL, js_URL=js_URL, chatlog=chatlog, players=return_data[1], stats=return_data[2], statistics=return_data[3], game_details=return_data[4], chart_title=chart_title, chart_link=chart_link, chart_link_ID=chart_link_ID)
        
    else:
        css_URL = url_for("static", filename="home.css")
        home_template = env.get_template("home.html")
        return home_template.render(cssURL=cssURL)

