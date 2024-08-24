from urllib.request import urlopen
import urllib
import json
import os
import random
import time
#import ctypes
#ctypes.windll.kernel32.SetConsoleTitleW("Auto Favourite Script H2M")


        

def de_dupe(x):
    return list( dict.fromkeys(x) )
  
def update_list():
    # its H2M because its loading all the H2M servers
    game = "H2M"
    #special characters to get rid of from the host name
    filterFromName = ["^:","^1","^2","^3","^4","^5","^6","^7","^8","^9","^0","^"]

    #Init the Blacklisted and Whitelisted Host lists
    #Whitelisted will always appear unless filtered out by low player counts
    blacklist = []
    whitelist = []
    #for servers that have some slots for premium members, to be filled as i discover
    privilegedHosts = []
    privilegedHosts += ["h2m-fr","mw2 remasterd","namelessnoobs","Kat-Net"]
    
    useMasterListWorkaround=False #if raidmax is down theres another website with the same server list
    
    limitPlayerCount=True #only show servers that have some players and free slots, only when live data is in use
    #NOTE: servers that meet the criteria will be more likely to show up over the servers that failed to meet the criteria
    minPlayers = 3 #minimum amount of players on a server
    minFreeSlots = 2 #minimum amount of free slots
    privilegedMinFreeSlots = 6 #minimum amount of free slots on a privileged server
    DiscardFailedLimit=False #Display servers that fail to meet above criteria (F/T), if false they'll be the last servers to appear
    LowestPriorityFailedPrivMinFreeIgnore=False #same but for privileged servers
    LowestPriorityFailedPrivMinFree=True #should privileged servers that fail the min player count show up dead last
    #Servers with premimum member slots but fail the minimal count are usually more worthless, Than other servers
    PreferWhitelisted=False #If Whitelisted should get preferential treatment, will not override priviliged low priority
    PreferNotEnoughFreeSlots=True #should servers that failed the minFreeSlots be prefered over ones that failed minPlayers
    PreferNotEnoughFreeSlotsAutoSwitch=True #should the option disable itself after x amount of players are online
    PreferNotEnoughFreeSlotsAutoSwitchPlayers=1250
    ShowOnlyVanillaGameplayServers=True #Show only vanillaish servers
    DontShowTrickshotServers=True
    DontShowExcessiveXPServers=True #Show servers with excessive xp
    DontShow2XPServers=False #Show servers that have 2XP on, most have 2xp
    
    #There is a 100 server display limit list on the server browser
    #But some servers dont show up there
    #I'm using 110 because the edge case of all 100 servers showing up is rather low
    saveServerCount = 110
    
    
    #private servers
    blacklist += ["private","reserved only"]
    
    #set of filters meant to create an as vanilla mw2 experience as possible
    if ShowOnlyVanillaGameplayServers:
        #no sniper servers
        blacklist += ["no snipers","no snipes","snipers banned","snipers disabled"]
        #no killstreak servers
        blacklist += ["no streaks","no killstreaks","no ks","uav only","uavs only","kill streaks off"]
        #servers where the nuke doesnt work properly
        blacklist += ["no nukes","moab"]
        #feels like cheating esp with no streaks
        blacklist += ["constant uav"]
        #anticamp, read as you get kicked if you stay in the same spot for 30 secs
        blacklist += ["anticamp","anti-camp"]
        #or grenades and such are banned
        blacklist += ["no bombs","no explosives","no frags","no stuns", "no tubes"]
        #servers with this usually go for excessive modifications
        blacklist += ["no bullshit","no bs"]
    if DontShowTrickshotServers:
        #trickshotting only servers
        blacklist +=["trickshot","snipers only","sniper only","only sniper","sniper lobby","sniping","tricky myers","team sniper"]
        blacklist += ["the club"] #trickshot s&d server
    if DontShowTrickshotServers and ShowOnlyVanillaGameplayServers:
        blacklist +=["sniper"] #extremely catch all term, will collide with no snipers
    if DontShow2XPServers:
        blacklist += ["x xp","x exp"]
        blacklist += ["x2 xp","2x xp","2xp","xxp","double xp","x2 exp"]
    if DontShowExcessiveXPServers:
        blacklist += ["high xp","high exp","fastlvl","fastxp","fastexp"]
        blacklist += ["x3 xp","3x xp","3xp","xxxp","triple xp","x3 exp"]
        blacklist += ["x4 xp","4x xp","4xp","xxxxp","quad xp","x4 exp"]
        blacklist += ["x5 xp","5x xp","5xp","xxxxxp","x5 exp"]
        blacklist += ["x6 xp","6x xp","6xp","xxxxxxp","x6 exp"]
        blacklist += ["x7 xp","7x xp","7xp","xxxxxxxp","x7 exp"]
        blacklist += ["x7 xp","7x xp","7xp","xxxxxxxxp","x8 exp"]
    
    #I just dont have good ping to those regions
    #blacklist += ["latam","asia","[au]","au/nz","xevnet.au","oce","(au)","mw2og","cn","brasil","brazil","maniacos","southern africa","[SA]","argentino","[BR]"]
    #blacklist += ["na south","[na-west]","us-west"]
    #hosts i had good prior experiences with + decent ping
    #whitelist += ["[hgm]","hazeynetwork","zedkaysserver","eu","uk","[bnuk]","cws","mysteriousryan","crwn"]
    
    # pingTest = True
    # pingLimit = 250
    # pingDict = {}
    # if os.path.exists("pings.json"):
        # pingDictJson = open('pings.json',"r")
        # pingDict = json.load(pingDictJson)
        # pingDictJson.close()



    #Header to bypass 403 forbidden
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    IW4MadminData = ""
    IW4MadminResponse = ""
    #locally downloaded instance data from https://master.iw4.zip/instance/
    #if IW4MAdmin api is down
    isLocal = os.path.exists("download.json")
    if isLocal:
        print("Found local data...")
        scraped = open('download.json',"r")
        IW4MadminData = json.load(scraped)
        scraped.close()
    else:
        # iw4madmin master server api
        # instance endpoint contains all the data in a json format
        # opening the url
        
        
        print("Attempting to connect to the iw4madmin master server...")
        if useMasterListWorkaround:
            IW4MadminURL = "https://master.iw4.zip/instance/"
            IW4MadminRequest = urllib.request.Request(IW4MadminURL, None, header)
            IW4MadminResponse = urlopen(IW4MadminRequest)
        else:
            IW4MadminURL = "http://api.raidmax.org:5000/instance/"
            IW4MadminResponse = urllib.request.urlopen(IW4MadminURL)
        IW4MadminData = json.loads(IW4MadminResponse.read())
        random.shuffle(IW4MadminData)
        print("Successfully connected and loaded data")
        #if(limitPlayerCount):
        #    print("Minimum playercount: {}".format(minPlayers))
        #    print("Minimum required slots: {}".format(minFreeSlots))
        #    print("Minimum required slots on privileged servers: {}".format(privilegedMinFreeSlots))
    
    
    

    #I shouldve made them dequeues but its late now
    ips = []    #Nonwhitelisted hosters
    ipsWhitelist = [] #Whitelisted hosters
    ipsFailedLimit = [] #failed to reach the limit
    ipsWhitelistFailedLimit = []
    ipsPrivFailedLimit = []
    fullServerCount = 0
    #Change all filters to be in lowercase
    blacklist = [x.lower() for x in blacklist]
    whitelist = [x.lower() for x in whitelist]
    privilegedHosts = [x.lower() for x in privilegedHosts]
    filterFromName = [x.lower() for x in filterFromName]
    print("Combing through the data...\n")
    
    if PreferNotEnoughFreeSlotsAutoSwitch:
        playerCount=0
        #If I built this with some hindsight I would've done it better
        #However this still works fast enough for my usecase and its a temporary measure
        for data in IW4MadminData:
            for server in data["servers"]:
                if(server["game"]==game):
                    hostnameCheck = server["hostname"].lower()
                    blacklisted = False
                    for undesirable in filterFromName: #Remove special characters
                        hostnameCheck = hostnameCheck.replace(undesirable, '')
                    blacklisted = any(ele in hostnameCheck for ele in blacklist)
                    if blacklisted:
                        continue
                    if server["ip"]=="localhost":
                        continue
                    playerCount+=server["clientnum"]
        if playerCount>PreferNotEnoughFreeSlotsAutoSwitchPlayers:
            PreferNotEnoughFreeSlots=False
        print("Total players online: {}".format(playerCount))
                
    
    # iterating over all the data
    for data in IW4MadminData:
        # iterating over only the servers
        for server in data["servers"]:
            # if we stumble upon a H2M gameserver
            if(server["game"]==game):
                # ping = 0
                # if server["ip"] in pingDict: #Check if the ping has been tested
                    # ping = pingDict.get(server["ip"])
                # else: #If it wasnt test it and save it
                    # ping = pingTestFunc(server["ip"],5)
                    # pingDict.update({server["ip"]: ping})
                    # f = open("pings.json", "w")
                    # json_string = json.dumps(pingDict)
                    # f.writelines(json_string)
                    # f.close()
                    # print("Pinged {0}, avg ping {1}".format(server["ip"],ping))
                if server["ip"]=="localhost": #Some idiots have their servers listed under localhost, ignore
                    continue
                fullServerCount+=1
                #we start checking the server name
                hostnameCheck = server["hostname"].lower()
                ip = server["ip"]+":"+str(server["port"])
                blacklisted = False
                whitelisted = False
                for undesirable in filterFromName: #Remove special characters
                    hostnameCheck = hostnameCheck.replace(undesirable, '')
                blacklisted = any(ele in hostnameCheck for ele in blacklist)
                whitelisted = any(ele in hostnameCheck for ele in whitelist)
                privileged = any(ele in hostnameCheck for ele in privilegedHosts)
                #if its a blacklisted host, ignore
                if blacklisted:
                    continue   
                #Whitelisted get special treatment
                if whitelisted:
                    if not isLocal and limitPlayerCount: #If we have the things enabled
                        if(server["clientnum"]<=minPlayers):
                            if PreferWhitelisted:
                                ipsWhitelistFailedLimit.append(ip)
                            else:
                                ipsFailedLimit.append(ip)
                            continue
                        if(server["maxclientnum"]-server["clientnum"]<=minFreeSlots):
                            if PreferWhitelisted:
                                if PreferNotEnoughFreeSlots:
                                    ipsWhitelistFailedLimit.insert(0, ip)
                                    continue
                                ipsWhitelistFailedLimit.append(ip)
                                continue
                            elif PreferNotEnoughFreeSlots:
                                ipsFailedLimit.insert(0, ip) #Dont be me, use dequeues instead, thankfully during low playercount hours this will only get hit like 20 times instead of 120 times
                                continue
                            else:
                                ipsFailedLimit.append(ip)
                            continue
                        if(server["maxclientnum"]-server["clientnum"]<=privilegedMinFreeSlots) and privileged:
                            if LowestPriorityFailedPrivMinFreeIgnore:
                                continue
                            if LowestPriorityFailedPrivMinFree:
                                ipsPrivFailedLimit.append(ip)
                            elif PreferWhitelisted:
                                ipsWhitelistFailedLimit.append(ip)
                            else:
                                ipsFailedLimit.append(ip)
                            continue
                    ip = server["ip"]+":"+str(server["port"])
                    ipsWhitelist.append(ip)
                    continue
                if not isLocal and limitPlayerCount:
                    if(server["clientnum"]<=minPlayers):
                        ipsFailedLimit.append(ip)
                        continue
                    if(server["maxclientnum"]-server["clientnum"]<=privilegedMinFreeSlots) and privileged:
                        if LowestPriorityFailedPrivMinFreeIgnore:
                            continue
                        if LowestPriorityFailedPrivMinFree:
                            ipsPrivFailedLimit.append(ip)
                        else:
                            ipsFailedLimit.append(ip)
                        continue
                    if(server["maxclientnum"]-server["clientnum"]<=minFreeSlots):
                        if PreferNotEnoughFreeSlots:
                            ipsFailedLimit.insert(0, ip)
                            continue
                        ipsFailedLimit.append(ip)
                        continue
                ips.append(ip)


    print("Saving...\n")
    # check if players2 exists, if not, create it
    isExist = os.path.exists("players2")
    if not isExist:
       os.makedirs("players2")
    print("Found {} servers, filtered down to {}".format(fullServerCount,len(ips)+len(ipsWhitelist)))
    # There is a 100 display limit, we gotta make sure we're under it otherwise weird stuff happens
    print("{} whitelisted, trimming total list".format(len(ipsWhitelist)))
    ipFiltered = []
    ipFiltered = ipsWhitelist + ips
    if not DiscardFailedLimit:
        ipFiltered = ipFiltered + ipsWhitelistFailedLimit+ ipsFailedLimit + ipsPrivFailedLimit
        

    # now we just write into the favorite servers file
    # and thats it

    # yes i know there's a better way but i want to play as well
    #Last sanity check for dupes, leftover just in case + trimming list
    de_duped=de_dupe(ipFiltered[:saveServerCount])
    #eh just in case it's region/locale dependant
    f = open("players2/favourites.json", "w")
    f.writelines(str(de_duped).replace("', '",'","').replace("']",'"]').replace("['",'["'))
    f.close()
    f = open("players2/favorites.json", "w")
    f.writelines(str(de_duped).replace("', '",'","').replace("']",'"]').replace("['",'["'))
    f.close()
    print("Saved {} servers to players2/favourites.json".format(len(de_duped)))

#Direct pinging experiment, doesnt work most of the time, ignore for now

# #Latency testing requires ping3 libary
# #comment out if latency tests arent necessary
# #and set pingTest to False
# from ping3 import ping

# def pingTestFunc(ip,count):
    # i = 0
    # latencySum = 0
    # while i<count:
        # latency = ping(ip)
        # if latency is None or latency is False:
            # latency = 999
        # latencySum+=latency
        # i+=1
    # latencySum/=i
    # return latencySum
    
if __name__ == "__main__":
    while True:
        update_list()
        time.sleep(random.randrange(31, 41))
