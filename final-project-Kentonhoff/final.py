import unittest
import sqlite3
import requests
import json
import matplotlib.pyplot as plt



#print(data)
CACHE_FNAME = "KenStarcraftCache.json"


try:
    cache_file = open(CACHE_FNAME, "r", encoding = "utf-8")
    cache_contents = cache_file.read()
    cache_file.close()
    cacheDict = json.loads(cache_contents)
except:
    response = requests.get('https://us.api.blizzard.com/sc2/ladder/grandmaster/1?access_token=US1gGr4FaVEV1He4B0yB2SP8czXb0qhhTh')
    data= response.json()
    dumped_json_cache = json.dumps(data)
    fw = open(CACHE_FNAME, "w", encoding = "utf-8")
    fw.write(dumped_json_cache)
    fw.close()

    cache_file = open(CACHE_FNAME, "r", encoding = "utf-8")
    cache_contents = cache_file.read()
    cache_file.close()
    cacheDict = json.loads(cache_contents)

"""Tries to read the cache. If it doesn't exist, makes a request to the API which returns the top 200 players on the leaderboard.

It then writes the data into the cache, closes it, then reopens it to read it.
"""

conn = sqlite3.connect('/Users/A/Desktop/si206/final-project-Kentonhoff/Players.sqlite')
cur = conn.cursor()

""" Creates the database connection to players.sqlite and the cursor."""


def setupplayertable(cacheDict, conn, cur):
    """ Takes the cache, a sqlite connection object, and a cursor and inserts the player information in the database.

    First creates a database players.sqlite if it doesn't exist. Then loads all the players into a table called Players, with the following columns in each row:
    display_name - contains the display name of the player on the leaderboard. the displayname is unique, so it will replace old values if it finds a new display_name that's the same.
    favorite_race - contains the favorite race of the player on the leaderboard. If a player does not have a favorite race, sets it to random.
    points - contains the point value of a player on the leaderboard.
    wins - contains the number of wins a player has on the leaderboard.
    losses- contains the number of losses a player has on the leaderboard.
    """

    cur.execute("CREATE TABLE IF NOT EXISTS Players(display_name TEXT UNIQUE, favorite_race TEXT, points INTEGER, wins INTEGER, losses INTEGER)")
    for ladder in cacheDict["ladderTeams"]:
        for player in ladder["teamMembers"]:
            display_ = player["displayName"]
            try:
                favorite_ = player["favoriteRace"]
            except:
                favorite_ = "random"
            point = ladder["points"]
            win = ladder["wins"]
            loss = ladder["losses"]
            cur.execute("INSERT OR REPLACE INTO players (display_name, favorite_race, points, wins, losses) VALUES (?, ?, ?, ?, ?)", (display_, favorite_, point, win, loss))

    conn.commit()

def getrace(cur):
    """ Gets data from the Players database and prints the number of players per race and the average win percentage per race.

    Takes a database cursor as input, selects the favorite_race, wins and losses from the players table in Players.sqlite
    Fetches all the results in the table.
    Creates 4 empty lists, one for each race and one for random, used to store each player's win percentage.
    For each row in the results, it turns the row into a list.
    Calculates the win percentage for each player by dividing the number of wins by the sum of wins and losses, then multiplies the answer by 100
    Determines what race they were playing by looking at the first element in the list.
    Appends that player's win percentage to the appropriate race list.
    The average for each list is calculated by taking the sum of the list divided by the length.
    A bar graph is then created using the race names as an x label and the win percentages as the y label.
    Prints out the number of players in each list and their average win percentage.
    """
    cur.execute("SELECT favorite_race, wins, losses FROM Players")
    results = cur.fetchall()
    protosswinpercent = []
    zergwinpercent = []
    terranwinpercent = []
    randomwinpercent = []

    for row in results:
        info=list(row)
        numwin = int(info[1])
        numloss= int(info[2])
        winpercent = (numwin/(numwin + numloss))*100

        if info[0] == 'protoss':
            protosswinpercent.append(winpercent)

        elif info[0] == 'zerg':
            zergwinpercent.append(winpercent)

        elif info[0] == 'terran':
            terranwinpercent.append(winpercent)

        else:
            randomwinpercent.append(winpercent)


    avgprotosswin = (sum(protosswinpercent)/len(protosswinpercent))
    avgzergwin = (sum(zergwinpercent)/len(zergwinpercent))
    avgterranwin = (sum(terranwinpercent)/len(terranwinpercent))
    avgrandomwin = (sum(randomwinpercent)/len(randomwinpercent))
    Race = ["Protoss", "Zerg", "Terran", "Random"]
    Racewinpercent = [avgprotosswin, avgzergwin, avgterranwin, avgrandomwin]
    pr, ze, te, ra = plt.bar(Race, Racewinpercent)
    pr.set_facecolor("b")
    ze.set_facecolor("m")
    te.set_facecolor("g")
    ra.set_facecolor("r")
    plt.xlabel("Type of Race")
    plt.ylabel("Average Win Percentage")
    plt.title("Bar graph of Starcraft 2 Leaderboard Races")
    plt.show()


    print("Number of Protoss players: " + str(len(protosswinpercent)))
    print("Average Protoss win percentage: " + str(avgprotosswin))
    print("-----------------------------")

    print("Number of Zerg players: " + str(len(zergwinpercent)))
    print("Average Zerg win percentage: " + str(avgzergwin))
    print("------------------------------")

    print("Number of Terran players: " + str(len(terranwinpercent)))
    print("Average Terran win percentage: " + str(avgterranwin))
    print("------------------------------")

    print("Number of Random players: " + str(len(randomwinpercent)))
    print("Average Random win percentage: " + str(avgrandomwin))
    print("------------------------------")

def getwins(cur):
    """ Gets data from the Players database and creates a bar graph with number of matches played vs win percentage.

    Takes a database cursor as input, selects the wins and losses from the players table in Players.sqlite
    Fetches all the results in the table.
    Creates 4 empty lists, one for each range of matches played (Less than 100 matches, 100-200 matches, 200-300 matches, more than 300).
    For each row in the results, it turns the row into a list.
    Calculates the win percentage for each player by dividing the number of wins by the sum of wins and losses, then multiplies the answer by 100
    Calculates the number of matches played by adding the number of wins to losses.
    Determines how many matches they played based on value calculated above.
    Appends that player's win percentage to the appropriate list based on number of matches played.
    The average for each list is calculated by taking the sum of the list divided by the length.
    A bar graph is then created using the number of matches played as an x label and the win percentages as the y label.
    """
    cur.execute("SELECT wins, losses FROM players")
    result = cur.fetchall()
    lessthan100 = []
    for100to200= []
    for200to300 = []
    plus300 = []
    for row in result:
        info=list(row)
        numwin = int(info[0])
        numloss= int(info[1])
        winpercent = (numwin/(numwin + numloss))*100
        matchesplayed = (numwin + numloss)
        if matchesplayed <= 100:
            lessthan100.append(winpercent)
        elif matchesplayed > 100 and matchesplayed <= 200:
            for100to200.append(winpercent)
        elif matchesplayed > 200 and matchesplayed <= 300:
            for200to300.append(winpercent)
        elif matchesplayed > 300:
            plus300.append(winpercent)


    avglessthan100 = (sum(lessthan100)/len(lessthan100))
    avg100to200 = (sum(for100to200)/len(for100to200))
    avg200to300 = (sum(for200to300)/len(for200to300))
    avgplus300 = (sum(plus300)/len(plus300))
    playedmatches = ["Less than 100", "100-200", "200-300", "More than 300"]
    playedwinpercent = [avglessthan100, avg100to200, avg200to300, avgplus300]
    on, tw, thr, plus = plt.bar(playedmatches, playedwinpercent)
    on.set_facecolor("c")
    tw.set_facecolor("y")
    thr.set_facecolor("r")
    plus.set_facecolor("g")
    plt.xlabel("Number of matches played")
    plt.ylabel("Average Win percent")
    plt.title("Bar graph of Starcraft 2 Leaderboard wins vs. matches")
    plt.show()






setupplayertable(cacheDict, conn, cur)
getrace(cur)
getwins(cur)
""" Calls all the functions."""
