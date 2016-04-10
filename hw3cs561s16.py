#!/usr/bin/python

import sys
import copy

InFname  = sys.argv[2]
OutFname = 'output.txt' 
queries  = list()
network  = dict()

#==============================================================================
class Node:
    '''Reperesents Node of Bayesian Network '''
    def __init__(self, name, parent, table):
        self.name   = name
        self.parent = copy.copy(parent)
        self.table  = copy.copy(table)
        # Processing
        self.__process__()

    def __process__(self):
        pass
        #print 'Name: ', self.name
        #print 'Parents:', self.parent
        #print 'Table: ', self.table

#==============================================================================
def makeNode(name, parent, table):
    # This function exists coz not all names are nodes. Preprocessing required.
    obj = Node(name, parent, table)
    network[name] = obj

#==============================================================================
def getNode(fhand):
    # First line of the node gives node and relationship
    relationship = fhand.readline().strip()
    if not relationship: return False
    relationship = relationship.split('|')
    name, parent, table = relationship[0].strip(), [], []
    # If len(relationship) == 1, No parent
    if len(relationship) == 1:
        table = [fhand.readline().strip()]
    else:
        # Parents
        parent = relationship[1].strip()
        parent = parent.split()
        # Conditional Probability Table
        for x in range(pow(2, len(parent))):
            table.append(fhand.readline().strip())
    # End of if else statement

    # Expecting '***' now. So just ignore that.
    fhand.readline()
    makeNode(name, parent, table)
    return True

#==============================================================================
def getNetwork(fhand):
    while True:
        status = getNode(fhand)
        if not status: break

#==============================================================================
def getQueries(fhand):
    # Getting list of all queries.
    while True:
        line = fhand.readline().strip()
        if line == '******': break
        queries.append(line)

#==============================================================================
def getData(fname):
    fhand = open(fname, 'r')
    getQueries(fhand)
    # Getting Bayesian Network
    getNetwork(fhand)

#==============================================================================
def trigger(name, known):
    print name
    print known

#==============================================================================
def getProbability(q):
    q = q.split('|')
    # Start of IF
    if len(q) == 1:
        q = q[0].split(',')
    else:
        q[1:] = q[1].split(',')
    # END of IF
    known = list()
    # Start of FOR
    for x in q:
        x = x.split(' = ')
        for index in range(len(x)):
            x[index] = x[index].strip()
        known.append(x)
    # END of FOR
    # Trigger Tree
    trigger(known[0][0], known)

#==============================================================================

if __name__ == '__main__':
    getData(InFname)
    for q in queries:
        if q.startswith('P'):
            getProbability(q[2:-1])
#==============================================================================
