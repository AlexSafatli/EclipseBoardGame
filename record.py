# record.py
# -------------------------
# Fall 2012; Alex Safatli
# -------------------------
# Software package for handling
# the recording and calculating
# of player scores for the Eclipse
# board game, along with keeping
# track of individual matches.

# Imports

import os, cPickle, datetime

# Match class. Encapsulates a match.

class match():
    
    def __init__(self,participants,results):       
        self.participants = participants # All players that participated and their roles.
        self.results = results # Final VP counts,
        self.timestamp = datetime.datetime.now()
        self.date = self.timestamp.strftime("%Y-%m-%d")
        self.maxvp = max(results.values())
        self.changes = {}
        
    def __str__(self):
        plyrs = ', '.join(self.participants.keys())
        return '[%s] %s' (self.date,plyrs)
    
# Player class. Encapsulates a player.

class player():
    
    def __init__(self,name,score=1200):
        self.name = name
        self.score = score
        
    def __str__(self):
        return self.name
    
# Score processing.

class scores():
    
    def __init__(self,playerdb,matchdb):
        
        def loadData(fn):
            fh = open(fn,'r')
            dt = cPickle.load(fh)
            fh.close()
            return dt
        
        self.playerdb = playerdb
        self.matchdb = matchdb
        self.players = {}
        self.matches = []
        if os.path.isfile(playerdb):
            self.players = loadData(playerdb)
        if os.path.isfile(matchdb):
            self.matches = loadData(matchdb)
    
    def update(self):
        
        def dumpData(fn,db):
            fh = open(fn,'w')
            cPickle.dump(db,fh)
            fh.close()
        
        # Update both databases.
        dumpData(self.playerdb,self.players)
        dumpData(self.matchdb,self.matches)
    
    def numGames(self,player):
        # Count the number of games for player.
        num = 0
        if player not in self.players:
            return 0
        for m in self.matches:
            if player in m.participants:
                num += 0
        return num
    
    def processMatch(self,match):
        maxvp = match.maxvp
        for player in match.participants:
            # See how much of a score increase.
            vp = match.results[player]
            modifier = 1.0 - 0.2*((maxvp-vp)/(maxvp/10.0))
            c = self.changeScore(player,modifier)
            match.changes[player] = c
        self.matches.append(match)
        self.update()
        
    def changeScore(self,player,modifier):
        if player not in self.players:
            # Default player score.
            self.players[player] = 100
        numgames = self.numGames(player)
        incre = int(11*(1-(numgames+1)/1000.0))
        if incre < 1:
            incre = 1
        change = int(incre*modifier)
        self.players[player] += change
        self.update()
        return change
            