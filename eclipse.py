# eclipse.py
# -------------------------
# Winter 2013; Alex Safatli
# -------------------------
# Software API for the Eclipse
# board game.

import random

# ------- Eclipse constructs ----------------

class die():
    # Encapsulates a 6-sided die.
    
    def __init__(self):
        self.value = self.roll()
    
    def roll(self):
        self.__die__ = random.randint(1,6)
        return self.__die__
    
    def __str__(self):
        return str(self.value)

class map():
    
    def __init__(self,numPlayers):
        pass

class system():
    # Encapsulates a single system hex.
    
    def __init__(self,wormholes,planets,ancient,discovery):
        # Wormholes is a length-6 boolean array indicating
        # if a given side of the hexagon, starting from top-most
        # and moving clockwise, has a wormhole.
        self.wormholes = wormholes
        for v in self.wormholes:
            if (v != 0) and (v != 1):
                raise ValueError('Wormhole array has non-boolean value.')
        # Planets is a list of possible planets in the system.
        self.planets = planets
        # Ancient is an ancient object if one is present.
        self.ancient = ancient
        # Discovery is a boolean: whether or not a discovery is present.
        
        
class planet():
    # Encapsulates a single planet.
    
    def __init__(self,money,science,materials):
        if money < 0 or science < 0 or materials < 0:
            raise ValueError('Cap value is negative.')        
        self.moneyCap = money
        self.moneyInhabitants = []
        self.scienceCap = science
        self.scienceInhabitants = []
        self.materialsCap = materials
        self.materialsInhabitants = []
        
    def inhabit(self,pop):
        if pop.type == 'money':
            MI, MC = self.moneyInhabitants, \
                self.moneyCap
            if len(MI) <= MC:
                MI.append(pop)
        elif pop.type == 'science':
            SI, SC = self.scienceInhabitants, \
                self.scienceCap
            if len(SI) <= SC:
                SI.append(pop)
        elif pop.type == 'materials':
            MaI, MaC = self.materialsInhabitants, \
                self.materialsCap
            if len(MaI) <= MaC:
                MaI.append(pop)
        else:
            raise TypeError('Population type invalid.')
    
    def isInhabitated(self):
        M,S,Ma = self.moneyInhabitants, \
            self.scienceInhabitants, \
            self.materialsInhabitants
        return not (len(M) == 0 and len(S) == 0 \
                and len(Ma) == 0)
    
class population():
    # Encapsulates a population for a race.
    
    def __init__(self,race,color,type):
        self.race = race
        self.color = color
        self.type = type
        
class spaceship():
    # Encapsulates any sort of spaceship unit.
    
    def __init__(self,slots,weapons,hulls,\
                 shields,drives,sources,computers):
        # How many slots are available.
        self.slots = slots
        if slots >= 0:
            if len(weapons) + len(hulls) + len(shields) \
               + len(drives) + len(sources) > slots:
                raise StandardError(\
                    'Too many items for number of slots.')
        else:
            slots = len(weapons) + len(hulls) + len(shields) \
                + len(drives) + len(sources) 
        # All weapons the ship possesses.
        self.weapons = weapons
        # All hulls the ship possesses.
        self.hulls = hulls
        # All shields the ship possesses.
        self.shields = shields
        # All drives the ship possesses.
        self.drives = drives
        # All sources the ship possesses.
        self.sources = sources
        # All computers the ship possesses.
        self.computers = computers
        # Effective health of ship.
        self.resetHealth()
        # Effective initiative of ship.
        self.getInitiative()
        # Effective power of ship determined.
        self.availablePower()

    def resetHealth(self):
        # Calculates and resets effective health
        # to maximum.
        self.health = sum([h.modifier for h in self.hulls]) + 1
        return self.health
    
    def getHealth(self):
        return self.health
    
    def reload(self):
        # Reload all weaponry.
        for w in self.weapons:
            w.reload()
    
    def getInitiative(self):
        self.initiative = 0
        for s in self.sources:
            self.initiative += s.init
        for s in self.drives:
            self.initiative += s.init
        for s in self.computers:
            self.initiative += s.init
        return self.initiative
    
    def availablePower(self):
        
        def calcUsed(dic):
            used = 0
            for it in dic:
                used += dic[it][0]
            return used
        
        power = sum([s.power for s in self.sources])
        costs = {}
        for w in self.weapons:
            costs[w] = (w.power,self.weapons)
        for h in self.hulls:
            costs[h] = (h.power, self.hulls)
        for s in self.shields:
            costs[s] = (s.power, self.shields)
        for d in self.drives:
            costs[d] = (d.power, self.drives)
        for c in self.computers:
            costs[c] = (c.power, self.computers)
        used = calcUsed(costs)
        while (used > power):
            # Remove items until all items have sufficient power.
            minv = min(costs.items(),key=lambda x: x[1][0])
            for it in costs:
                if costs[it][0] == minv:
                    costs[it][1].remove(it)
                    del costs[it]
                    used = calcUsed(costs)
                    break
        return power - used
        
    def isDead(self):
        return (self.health <= 0)
        
    def hasOpenSlot(self):
        return (len(self.weapons) + len(self.hulls) + \
               len(self.shields) + len(self.drives) + \
               len(self.sources) < self.slots)
    
    def hasCombatLayer(self,cmbt):
        # See if any weapons have this layer.
        for w in self.weapons:
            if w.cmbt == cmbt:
                return True
        return False
    
    def rollDamage(self,cmbt=0):
        # Take into account the effect of
        # computers.
        modifier = sum([c.modifier for c in self.computers])
        hits = []
        # Get raw rolls from weapons.
        for w in self.weapons:
            if w.cmbt != cmbt:
                continue
            rollarr = w.roll()
            # See if hit.
            for roll in rollarr:
                if (roll == 6): # Automatic hit.
                    hits.append([roll,w.dmg,1])
                elif (roll != 1) and (roll + modifier >= 6):
                    hits.append([roll+modifier,w.dmg,0])
        return hits
    
    def takeDamage(self,hitarray):
        # Take into account the effect of
        # shields.
        modifier = sum([s.modifier for s in self.shields])
        dmg = 0
        # Takes an array of hits: (roll,damage,auto) tuples.
        for hit in hitarray:
            r, d, a = hit
            if (a) or (r - modifier >= 6):
                self.health -= d
                dmg += d
        return dmg # Total damage taken.
    
    def spacesCanMove(self):
        return sum([s.spaces for s in self.drives])
    
    def __repr__(self):
        return '<%s/%s>' % (self.__class__.__name__\
                            ,hex(id(self)))

class weapon():
    # Encapsulates a weapon.
    
    def __init__(self,dice,dmg,power=0,cmbt=0,limit=0):
        # The number of dice to roll.
        self.dice = dice
        # The damage each dice deals.
        self.dmg = dmg
        # Power this item requires to run.
        self.power = power
        # In relation to combat, when deals damage.
        self.cmbt = cmbt
        # Limit to how many times per combat can be used.
        self.limit = limit
        # Counter for how many times the weapon can fire.
        self.counter = limit
        
    def roll(self):
        num, dice = self.dice, die()
        dicearray = []
        for n in xrange(0,num):
            dicearray.append(dice.roll())
        self.counter -= 1
        if not self.limit == 0 and self.counter < 0:
            return []
        else:
            return dicearray
        
    def reload(self):
        self.counter = self.limit

class hull():
    # Encapsulates a hull.
    
    def __init__(self,mod,power=0):
        self.modifier = mod
        self.power = power
        
class shield():
    # Encapsulates a shield.
    
    def __init__(self,mod,power=0):
        self.modifier = mod
        self.power = power
        
class drive():
    # Encapsulates a drive.
    
    def __init__(self,spaces,power=0,init=0):
        self.spaces = spaces
        self.power = power
        self.init = init
        
class source():
    # Encapsulates a source.
    
    def __init__(self,power,init=0):
        self.power = power
        self.init = init

class computer():
    # Encapsulates a computer.
    
    def __init__(self,mod,power=0,init=0):
        self.modifier = mod
        self.power = power
        self.init = init
        
# ------- Eclipse literals ----------------

class gcd(spaceship):
    def __init__(self):
        spaceship.__init__(self,-1,[gcd_weapon()],[gcd_hull()],\
                           [],[],[],[electron_computer()])

class gcd_weapon(weapon):
    def __init__(self):
        weapon.__init__(self,4,1)
        
class gcd_hull(hull):
    def __init__(self):
        hull.__init__(self,7)
    
class ancient(spaceship):
    def __init__(self):
        spaceship.__init__(self,-1,[ancient_weapon()], \
                           [standard_hull()], [], [], \
                           [init2_source()], [electron_computer()])

class ancient_weapon(weapon):
    def __init__(self):
        weapon.__init__(self,2,1)

class init1_source(source):
    def __init__(self):
        source.__init__(self,0,1)

class init2_source(source):
    def __init__(self):
        source.__init__(self,0,2)

class init4_source(source):
    def __init__(self):
        source.__init__(self,0,4)

class terran_interceptor(spaceship):
    def __init__(self):
        spaceship.__init__(self,5,[ion_cannon()],[],[]\
                           ,[nuclear_drive()],[nuclear_source(),\
                                               init2_source()],[])

class terran_cruiser(spaceship):
    def __init__(self):
        spaceship.__init__(self,7,[ion_cannon()],[standard_hull()],[],\
                           [nuclear_drive()],[nuclear_source(),\
                                              init1_source()],\
                           [electron_computer()])

class terran_dreadnaught(spaceship):
    def __init__(self):
        spaceship.__init__(self,8,[ion_cannon(),ion_cannon()],\
                           [standard_hull(),standard_hull()],\
                           [],[nuclear_drive()],[nuclear_source()],\
                           [electron_computer()])
        
class terran_starbase(spaceship):
    def __init__(self):
        spaceship.__init__(self,7,[ion_cannon()],\
                           [standard_hull(),standard_hull()],\
                           [],[],[nuclear_source()],\
                           [electron_computer()])

class ion_cannon(weapon):
    def __init__(self):
        weapon.__init__(self,1,1,power=1)

class plasma_cannon(weapon):
    def __init__(self):
        weapon.__init__(self,1,2,2)

class plasma_missile(weapon):
    def __init__(self):
        weapon.__init__(self,2,2,cmbt=-1,limit=1)

class antimatter_cannon(weapon):
    def __init__(self):
        weapon.__init__(self,1,4,4)

class standard_hull(hull):
    def __init__(self):
        hull.__init__(self,1)

class improved_hull(hull):
    def __init__(self):
        hull.__init__(self,2)

class gauss_shield(shield):
    def __init__(self):
        shield.__init__(self,1)

class phase_shield(shield):
    def __init__(self):
        shield.__init__(self,2,power=1)

class nuclear_source(source):
    def __init__(self):
        source.__init__(self,3)

class fusion_source(source):
    def __init__(self):
        source.__init__(self,6)

class tachyon_source(source):
    def __init__(self):
        source.__init__(self,9)

class electron_computer(computer):
    def __init__(self):
        computer.__init__(self,1)

class positron_computer(computer):
    def __init__(self):
        computer.__init__(self,2,1,1)

class gluon_computer(computer):
    def __init__(self):
        computer.__init__(self,3,2,2)

class nuclear_drive(drive):
    def __init__(self):
        drive.__init__(self,1,1,1)

class fusion_drive(drive):
    def __init__(self):
        drive.__init__(self,2,2,2)

class tachyon_drive(drive):
    def __init__(self):
        drive.__init__(self,3,3,3)
        
