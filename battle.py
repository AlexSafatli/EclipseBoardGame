# battle.py
# -------------------------
# Winter 2013; Alex Safatli
# -------------------------
# Battle simulator for Eclipse
# boardgame. Requires Eclipse API.

import eclipse

def announce(targetter,dmg,target):
    print '%s did %d damage to %s.' % (targetter,dmg,target)
    if target.isDead():
        print '%s died with %d health.' % (target,target.getHealth())

class analysis():
    
    def __init__(self,fleet1,fleet2):
        self.f1 = fleet1
        self.f2 = fleet2
        self.f1_p = 0
        self.f2_p = 0
        
    def go(self,n=1000):
        f1, f2 = [], []
        
        def makeNewBattle(f1,f2):
            f1, f2 = [], []
            for p in self.f1:
                p.resetHealth()
                f1.append(p)
            for p in self.f2:
                p.resetHealth()
                f2.append(p)
            return f1, f2
        
        f1_w, f2_w = 0, 0
        for x in xrange(0,n):
            f1, f2 = makeNewBattle(f1,f2)
            b = battle(f1,f2,False)
            b.fight()
            f1_winner = True
            for i in b.winner():
                if i not in f1:
                    f2_w += 1
                    f1_winner = False
            if f1_winner:
                f1_w += 1
        self.f1_p = f1_w/float(n)
        self.f2_p = f2_w/float(n)
        
    def __str__(self):
        return 'f1: %.3f / f2: %.3f' % (self.f1_p,self.f2_p)

class battle():
    
    def __init__(self,p1,p2,verbose=True):
        
        def getInits():
            init = {}
            for s in p1:
                val = s.getInitiative()
                if val in init:
                    init[val].append((s,p2))
                else:
                    init[val] = [(s,p2)]
            for s in p2:
                val = s.getInitiative()
                if val in init:
                    init[val].append((s,p1))
                else:
                    init[val] = [(s,p1)]
            return init
        
        self.player1 = p1 # attacker
        self.player2 = p2 # defender
        self.verbose = verbose
        self.initiatives = sorted(getInits().items(),\
                                  key=lambda x:x[0])
        
    def manageDamage(self,ship,layer,enemies):
        dmg = ship.rollDamage(layer)
        enemyhps = [(s.getHealth(),s) for s in enemies]
        enemyhps = sorted(enemyhps,key=lambda x: x[0])
        enemy = enemyhps[0][1]
        out = enemy.takeDamage(dmg)
        if enemy.isDead():
            enemies.remove(enemy)
        return (out, enemy)
        
    def precombat(self):
        for ship in self.player1:
            if ship.hasCombatLayer(-1):
                dmg, shot = self.manageDamage(ship,-1,self.player2)
                if self.verbose:
                    announce(ship,dmg,shot)
        for ship in self.player2:
            if ship.hasCombatLayer(-1):
                dmg, shot = self.manageDamage(ship,-1,self.player1) 
                if self.verbose:
                    announce(ship,dmg,shot)
            
    def fight(self):
        
        def turn(ship,enemy):
            dmg, shot = self.manageDamage(ship,0,enemy)
            if self.verbose:
                announce(ship,dmg,shot)            
                
        self.precombat() # precombat
        while (len(self.player1) > 0 and len(self.player2) > 0):
            # Both sides still have ships.
            for s in self.initiatives:
                for i in s[1]:
                    ship, enemy = i
                    if (len(enemy) > 0) and \
                       (ship in self.player1 or ship in self.player2):
                        turn(ship,enemy)
                        
    def winner(self):
        if (len(self.player1) > 0 and len(self.player2) > 0):
            return None
        else:
            if len(self.player1) > 0:
                return self.player1
            else:
                return self.player2
                
fleetOne = [eclipse.gcd()]
fleetTwo = [eclipse.terran_dreadnaught(),eclipse.terran_cruiser()]
fleetTwo[0].shields.append(eclipse.gauss_shield())
fleetTwo[1].shields.append(eclipse.gauss_shield())
print 'fleetOne: %s' % (fleetOne)
print 'fleetTwo: %s\n\nBattle Analysis:\n' % (fleetTwo)
a = analysis(fleetOne,fleetTwo)
a.go()
print a