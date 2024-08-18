from urllib.request import urlopen
import urllib
import json
import os
import random
import time

def de_dupe(x):
    return list( dict.fromkeys(x) )
  
def update_list():
    # its H2M because its loading all the H2M servers
    game = "H2M"
    #special characters to get rid of
    filterFromName = ["^:","^1","^2","^3","^4","^5","^6","^7","^8","^9","^0","^"]

    #Blacklisted and Whitelisted Hosts
    #Whitelisted will always appear unless filtered out by low player counts
    #should be lowercase
    blacklist = []
    whitelist = []

    #minimal player count
    
    
    #show only servers that have some players and free slots
    #used only on live data
    #note, it will be slightly inaccurate, iw4madmin master server data is up to 30 secs out of date
    limitPlayerCount=True
    #minimum amount of players on a server
    minPlayers = 3
    #minimum amount of free slots
    minFreeSlots = 2
    #for servers that have some slots for premium members, to be filled as i discover
    privilegedHosts = ["h2m-fr","mw2 remasterd"]
    privilegedMinFreeSlots = 4
    #Completely ignore servers outside of bounds or add to the list at lowest priority
    DiscardFailedLimit=False
    #Servers with premimum member slots but fail the minimal count are usually more worthless
    #Than other servers
    LowestPriorityFailedPrivMinFree=True
    #If Whitelisted should get preferential treatment, will not override priviliged low priority
    PreferWhitelisted=False
    
    #There is a 100 server display limit list on the server browser
    #But some servers dont show up there
    #I'm using 110 because the edge case of all 100 servers showing up is rather low
    saveServerCount = 110

    #personal list, for context im from eu
    #I just dont have good ping to those regions + Trickshotting is not for me
    #blacklist = ["latam","asia","[au]","au/nz","xevnet.au","na south","oce","trickshot","(au)","snipers only","[na-west]","mw2og","CN"]
    #hosts i had good prior experiences with + decent ping
    #whitelist = ["[hgm]","hazeynetwork","zedkaysserver","eu","uk","op gold","[bnuk]","freak of duty","cws","MysteriousRyan","CRWN"]



    #Header to bypass 403 forbidden
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}


    IW4MadminData = ""
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
        
        IW4MadminURL = "https://master.iw4.zip/instance/"
        print("Attempting to connect to the iw4madmin master server...")
        #IW4MadminURL = "http://api.raidmax.org:5000/instance/"
        #IW4MadminResponse = urllib.request.urlopen(IW4MadminURL)
        IW4MadminURL = "https://master.iw4.zip/instance/"
        IW4MadminRequest = urllib.request.Request(IW4MadminURL, None, header)
        IW4MadminResponse = urlopen(IW4MadminRequest)
        # parsing the json and storing it
        IW4MadminData = json.loads(IW4MadminResponse.read())
        random.shuffle(IW4MadminData)
        print("Successfully connected and loaded data")
        if(limitPlayerCount):
            print("Minimum playercount: {}".format(minPlayers))
            print("Minimum required slots: {}".format(minFreeSlots))
            print("Minimum required slots on privileged servers: {}".format(privilegedMinFreeSlots))




    ips = []    #Nonwhitelisted hosters
    ipsWhitelist = [] #Whitelisted hosters
    ipsFailedLimit = [] #failed to reach the limit
    ipsWhitelistFailedLimit = []
    ipsPrivFailedLimit = []
    fullServerCount = 0
    print("Combing through the data...\n")
    # iterating over all the data
    for data in IW4MadminData:
        # iterating over only the servers
        for server in data["servers"]:
            # if we stumble upon a H2M gameserver
            if(server["game"]==game):
                fullServerCount+=1
                #we check the hostname
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
                #we check the playercount
                if whitelisted:
                    if not isLocal and limitPlayerCount:
                        if(server["clientnum"]<=minPlayers):
                            if PreferWhitelisted:
                                ipsWhitelistFailedLimit.append(ip)
                            else:
                                ipsFailedLimit.append(ip)
                            continue
                        if(server["maxclientnum"]-server["clientnum"]<=privilegedMinFreeSlots) and privileged:
                            if PreferWhitelisted:
                                ipsWhitelistFailedLimit.append(ip)
                            else:
                                ipsFailedLimit.append(ip)
                            continue
                        if(server["maxclientnum"]-server["clientnum"]<=minFreeSlots):
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
                        if LowestPriorityFailedPrivMinFree:
                                ipsPrivFailedLimit.append(ip)
                        else:
                            ipsFailedLimit.append(ip)
                        continue
                    if(server["maxclientnum"]-server["clientnum"]<=minFreeSlots):
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

if __name__ == "__main__":
    while True:
        update_list()
        time.sleep(random.randrange(31, 120)) #Big range as to not spam the server needlessly, also servers send out another heartbeat every 30 secs
