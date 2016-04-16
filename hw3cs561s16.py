#!/usr/bin/python
import sys
import re
import copy
import itertools
from optparse import OptionParser

#======================BEGINNING OF NETWORK CLASS==============================
class Network:

    # BEGINNING of CONSTRUCTOR
    def __init__ (self, fin, fout):
        # Need a data-structure to store all nodes
        self.net = dict()
        self.var = list()
        while True:
            status = self._getNode(fin)
            if not status: break
    # END of CONSTRUCTOR

    # BEGINNING of GET NODE
    def _getNode(self, fin):
        relationship = fin.readline().strip()
        if not relationship: return False
        relationship = relationship.split(' | ')

        name = relationship[0].strip()
        self.var.append(name)
        #self.net[name] = { 'parents' : [], 'prob' : 0.0, 'table': {} }

        if len(relationship) == 1:
            self.net[name] = { 'prob' : 0.0 }
            try:
                self.net[name]['prob'] = float(fin.readline().strip())
            except:
                self.net[name]['decision'] = True
        else:
            self.net[name] = { 'parents' : [], 'table': {} }
            self.net[name]['parents'] = relationship[1].strip().split()
            #***********************************************************#
            # How are we storing the probability table?
            for x in range(pow(2, len(self.net[name]['parents']))):
                line = fin.readline().strip().split()
                value= float(line[0])
                line = line[1:]
                for i in range(len(line)):
                    if line[i] == '+': line[i] = True
                    else: line[i] = False
                line = tuple(line)
                self.net[name]['table'][line] = value
            #***********************************************************#
        # Are we expecting utility node?
        #***************************************************************#
        if fin.readline().strip() == '******':
            relationship = fin.readline().strip()
            relationship = relationship.split(' | ')
            name = relationship[0].strip()
            self.net[name] = { 'parents' : [], 'table': {} }
            self.net[name]['parents'] = relationship[1].strip().split()
            #***********************************************************#
            # How are we storing the probability table?
            for x in range(pow(2, len(self.net[name]['parents']))):
                line = fin.readline().strip().split()
                value= float(line[0])
                line = line[1:]
                for i in range(len(line)):
                    if line[i] == '+': line[i] = True
                    else: line[i] = False
                line = tuple(line)
                self.net[name]['table'][line] = value
            #***********************************************************#
            '''
            print relationship
            print self.net[name]['parents']
            print self.net[name]['table']
            '''
        #***************************************************************#
        return True
    # END of GET NODE

    # BEGINNING of GET TABLE
    def getTable(self, name, value, eDict):
        # Decision Variables?
        if 'decision' in self.net[name]:
            return 1.0
        # Independent Variables?
        if 'prob' in self.net[name]:
            if value: return self.net[name]['prob']
            else: return 1 - self.net[name]['prob']
        # Conditional Variable
        match = list()
        #print self.net[name]['table']
        # We know that the parent belongs to eDict because it must have
        # been computed already.
        for parent in self.net[name]['parents']:
            #print parent
            #print eDict[parent]
            match.append(eDict[parent])
        match = tuple(match)
        #print match
        #print self.net[name]['table'][match]
        if value: return self.net[name]['table'][match]
        else: return 1 - self.net[name]['table'][match]
    # END of GET TABLE

    # BEGINNING of ENUMERATE ALL
    def enumerateAll(self, varList, eDict):
        '''
        print varList
        print eDict
        '''
        # Base Condition
        if not varList: return 1.0
        Y = varList[0]
        # If Y has value y in eDict
        if Y in eDict:
            #print Y
            # P(y|parent(Y))
            r1 = self.getTable(Y, eDict[Y], eDict)
            #print r1
            # Recursively Computing rest of the variables
            r2 = self.enumerateAll(varList[1:], eDict)
            #print r2
            return r1 * r2
        else:
            # True for first Iteration and false for next
            #print Y
            result = 0.0
            for y in [True, False]:
                r1 = self.getTable(Y, y, eDict)
                #print r1
                eDict[Y] = y
                r2 = self.enumerateAll(varList[1:], eDict)
                result += r1 * r2
                #print r2
            # This node is no more known.
            del eDict[Y]
            return result
    # END of ENUMERATE ALL

    # BEGINNING of JOINT ASK
    def jointAsk(self, query):
        query = query.split(', ')
        edict = dict()
        #*******************************************#
        for item in query:
            item = item.split(' = ')
            if item[1] == '+':
                edict[item[0].strip()] = True
            else:
                edict[item[0].strip()] = False
        #*******************************************#
        #print edict
        bn       = self.net
        varList  = self.var
        result   = self.enumerateAll(varList, edict)
        return result
    # END of JOINT ASK


    # BEGINNING of ENUMERATE ASK
    def enumerateAsk(self, query):
        X, var = query[0].split(' = ')
        edict  = dict()
        if var == '+': var = True
        else: var = False
        #********************************************#
        for item in query[1].strip().split(', '):
            item = item.split(' = ')
            if item[1] == '+':
                edict[item[0].strip()] = True
            else:
                edict[item[0].strip()] = False
        #********************************************#
        bn       = self.net
        varList  = self.var
        # Since we are dealing with boolean variables
        # First Part. (Computing for var)
        edict[X] = var
        r1 = self.enumerateAll(varList, edict)
        #print r1
        # Second part. (Computing for not var)
        edict[X] = not var
        r2 = self.enumerateAll(varList, edict)
        #print r2
        result = r1/(r1 + r2)
        return result
        #********************************************#
        '''
        edict[X] = not var
        r2 = self.enumerateAll(varList, edict)
        print X
        print edict
        print self.net
        '''
    # END of ENUMERATE ASK

    # BEGINNING of UTILITY ASK
    def utilityAsk(self, query):
        query = query.split(' | ')
        edict = dict()
        if len(query) > 1:
            query[1:] = query[1].split(', ')
        #********************************************#
        for item in query:
            item = item.split(' = ')
            if item[1] == '+':
                edict[item[0].strip()] = True
            else:
                edict[item[0].strip()] = False
        #********************************************#
        varList = self.var
        bn      = self.net
        '''
        edict[bn['utility']['parents'][0]] = True
        r1 = self.enumerateAll(varList, edict)
        r2 = 1.0 - r1
        r1 = r1 * bn['utility']['table'][(True,)]
        r2 = r2 * bn['utility']['table'][(False,)]
        print int(round(r1 + r2))
        '''
    # END of UTILITY ASK

#============================END OF NETWORK CLASS==============================

#=========================BEGINNING OF DRIVER CLASS============================
class Driver:
    # BEGINNING of CONSTRUCTOR
    def __init__(self, fname):
        self.fin     = open(fname, 'r')
        self.fout    = open('output.txt','w')
        self.queries = list()
        self.network = None
        # Getting Queries here
        self._getQueries()
        # Getting Network here
        self._getNetwork()
    # END of CONSTRUCTOR

    # BEGINNING of GET QUERIES
    def _getQueries(self):
        while True:
            line = self.fin.readline().strip()
            if line == '******': break
            self.queries.append(line)
    # END of GET QUERIES

    # BEGINNING of GET NETWORK
    def _getNetwork(self):
        # Creating NETWORK NODES
        self.network = Network(self.fin, self.fout)
    # END of GET NETWORK

    # BEGINNING of GET PROBABILITY
    def getProbability(self, query):
        # Conditional ?
        query = query.split(' | ')
        # Joint Probability / Maginal Probability
        if len(query) == 1:
            return self.network.jointAsk(query[0])
        else:
            return self.network.enumerateAsk(query)
    # END of GET PROBABILITY

    # BEGINNING of GET UTILITY
    def getUtility(self, query):
        return self.network.utilityAsk(query)
    # END of GET UTILITY

    # BEGINNING of LAUNCH
    def trigger(self):
        #***********************************************#
        for q in self.queries:
            if q.startswith('P'):
                result = self.getProbability(q[2:-1])
                result = format(result, '0.2f')
                self.fout.write(result)
                self.fout.write('\n')
            elif q.startswith('EU'):
                result = self.getUtility(q[3:-1])
            elif q.startswith('MEU'):
                pass
            else:
                print 'How did we end up here??'
        #***********************************************#
        # All the queries are handled, safe to close file
        self.fout.close()

    # END of LAUNCH

#=========================END OF DRIVER CLASS==================================

#========================TRIGGER============================
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", action="store", dest="fname")
    (option, args) = parser.parse_args()
    obj = Driver(option.fname)
    obj.trigger()
#====================END OF TRIGGER=========================
