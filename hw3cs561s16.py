#!/usr/bin/python

import sys

InFname  = sys.argv[2]
OutFname = 'output.txt' 
queries  = list()

#==============================================================================
class Node:
    '''Reperesents Node of Bayesian Network '''
    def __init__(self):
        pass

#==============================================================================
def makeNode(name, parent, table):
    print 'Name: ', name
    print 'Parents:', parent
    print 'Table: ', table

#==============================================================================
def getNode(fhand):
    # First line of the node gives node and relationship
    relationship = fhand.readline().strip()
    if not relationship: return False
    relationship = relationship.split('|')
    name, parent, table = relationship[0], [], []
    # If len(relationship) == 1, No parent
    if len(relationship) == 1:
        table = fhand.readline().strip()
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
if __name__ == '__main__':
    getData(InFname)
