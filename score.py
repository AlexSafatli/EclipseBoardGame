# score.py
# -------------------------
# Fall 2012; Alex Safatli
# -------------------------
# HTML and console interface
# for Eclipse scoring.

# Imports.

import sys, os, HTML
import record as r

# Functions.

def getData(partic,vps):
    line = ''
    while line != 'DONE':
        line = raw_input()
        items = line.split()
        if len(items) != 3:
            if line != 'DONE':
                print '>> Could not parse.'
        else:
            player, race, vp = items
            try:
                vp = int(vp)
            except:
                print '>> Could not parse.'
                continue
            partic[player] = race
            vps[player] = vp
            print '>> Parsed as player=%s, race=%s, vp=%s.' \
                  % (player,race,vp)

def makeHTML(s):
    html = '<html><body><p><strong>Players</strong></p>'
    header = ['Player','Score']
    tbl = []
    for p in s.players:
        tbl.append([p,s.players[p]])
    tblcode = HTML.table(tbl,header_row=header)
    html += tblcode
    header = ['Player','Race','VPs','VPs/players','Score Change']
    for m in s.matches:
        html += '<p><strong>match #%d</strong>: %s</p>' % (s.matches.index(m),m.date)
        tbl = []
        for p in m.participants:
            vp = m.results[p]
            tbl.append([p,m.participants[p],vp,'%.2f' \
                        % (float(vp)/len(m.participants)),\
                        str(m.changes[p])])
        tblcode = HTML.table(tbl,header_row=header)
        html += str(tblcode)
    html += '</body></html>'  
    return html

# Main.

if (len(sys.argv[1:]) != 2):
    print 'usage: python score.py playerfile matchfile'
    exit()
else:
    playerdb, matchdb = sys.argv[1:]

print 'On each line:\nInput player name, the race ' + \
      'they played,\nand the amount of VPs they won, ' + \
      'separated by spaces.\nType DONE to stop.\n'

partic = {} # Participant dictionary.
vps = {} # VPs dictionary.
getData(partic,vps) # Get input data.

s = r.scores(playerdb,matchdb) # Load databases.

if len(partic) != 0:
    # No data was input otherwise.
    m = r.match(partic,vps)
    s.processMatch(m)
    print '\nScores:'
    for p in m.changes:
        print '%s %d (%d)' % (p,s.players[p],m.changes[p])
else:
    print '\nScores:'
    for p in s.players:
        print '%s %d' % (p,s.players[p])

print '\n>> Parsing to %s.html.' % (matchdb)
html = makeHTML(s) # Convert to HTML (tables).
fh = open('%s.html'%(matchdb),'w')
fh.write(html)
fh.close()
