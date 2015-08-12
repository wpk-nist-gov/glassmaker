# recipe - recipe maker

import functions as F
import glass as G
import os
import json
import copy

class Recipe(object):
  def __init__(self):
    """Return a new object to represent a recipe for making a range of glass beads
      Each element posses the following, lists of two objects:
        beadFileName: file name describing beads to meld
        targetElement: desired element to obtain in percentage ranges
        percentMin: lower percentage, inclusive
        percentMax: higher percentage, inclusive
        percentInc: percentage increment from min to max """
    self._data = { "beadFileName" : [], "targetElement" : [], "percentMin" : [], "percentMax" : [], "percentInc" : [], "inventory" : [] }
    self._checkSizes()
    self._bead = []

  def _checkSizes(self):
    """Recipe is hard coded for two beads.
       Size of data elements must be 2, or 0 (not initialized) """
    beadLen = len(self._data["beadFileName"])
    targEleLen = len(self._data["targetElement"])
    percentMinLen = len(self._data["percentMin"])
    percentMaxLen = len(self._data["percentMax"])
    percentIncLen = len(self._data["percentInc"])
    if ( (beadLen != targEleLen) 
      or (beadLen != percentMinLen) 
      or (beadLen != percentMaxLen) 
      or (beadLen != percentIncLen) 
      or ( (beadLen != 0) and (beadLen != 2) ) ):
      raise RuntimeError("checkSize failed")
  
  def addElementWithBeadInRange(self, bead, targetElement, percentMin, percentMax, percentInc):
    """add a bead to the recipe"""
    self._bead.append(bead) 
    self._data["beadFileName"].append("bead"+str(len(self._data["beadFileName"])))
    self._data["targetElement"].append(targetElement)
    self._data["percentMin"].append(percentMin)
    self._data["percentMax"].append(percentMax)
    self._data["percentInc"].append(percentInc)
    if ((percentMax - percentMin) % percentInc > 1e-15):
      raise RuntimeError("percentMin/Max/Inc disagreement")

  def initInventory(self):
    """ build inventory matrix, assuming two beads to mix
     the matrix will keep track of which combinations of percentages were fabricated
      inventory[bead0per][bead1per] = 0 or 1 """
    nPercentValues0 = int((self._data["percentMax"][0] - self._data["percentMin"][0])/self._data["percentInc"][0] + 1)
    nPercentValues1 = int((self._data["percentMax"][1] - self._data["percentMin"][1])/self._data["percentInc"][1] + 1)
    for i in range(nPercentValues0):
      zeros = [0] * nPercentValues1
      self._data["inventory"].append(zeros)

  def writeJSON(self, fileName):
    """ write object to JSON file"""
    if (os.path.isfile(fileName+".json")):
      print "Warning: backing-up \""+fileName+".json"+"\" to \""+fileName+".json.bak\""
      os.rename(fileName+".json", fileName+".json.bak")
    with open(fileName+".json", 'w') as f:
      json.dump(self._data, f)
    for index in range(len(self._bead)):
      (self._bead[index]).writeJSON(fileName+self._data["beadFileName"][index])

  def readJSON(self, fileName):
    """ read glass object from JSON file"""
    with open(fileName+".json", 'r') as f:
      self._data = json.load(f)
    for index in range(len(self._data["beadFileName"])):
      bead = G.Glass()
      bead.readJSON(fileName+self._data["beadFileName"][index])
      self._bead.append(bead)
    self._checkSizes()

  def index2percent(self, bead, index):
    return self._data["percentMin"][bead] + self._data["percentInc"][bead]*index

  def percent2index(self, bead, percent):
    if ( (percent - self._data["percentMin"][bead]) % self._data["percentInc"][bead] > 1e-15):
      raise RuntimeError("invalid percent")
    return int((percent - self._data["percentMin"][bead]) / self._data["percentInc"][bead]) 

  def suggestNext(self):
    """ suggest creation of the next bead
    attempt to target the 'middle most' percentages """
    per0 = -1
    per1 = -1
    for ibead0 in range(len(self._data["inventory"])):
      for ibead1 in range(len(self._data["inventory"][0])): 
        if (per0 < 0 and per1 < 0):
          if (self._data["inventory"][ibead0][ibead1] == 0):
            per0 = self.index2percent(0, ibead0)
            per1 = self.index2percent(1, ibead1)
    print "Try to create a bead with",str(per0)+"%",self._data["targetElement"][0], "and with", str(per1)+"%", self._data["targetElement"][1]
 
  def addInventory(self, per0, per1):
    """ add bead with desired precentages to the inventory """
    print "Added bead with",str(per0)+"%",self._data["targetElement"][0], "and with", str(per1)+"%", self._data["targetElement"][1]
    self._data["inventory"][self.percent2index(0,per0)][self.percent2index(1,per1)] = 1

#    bead = 0
#    mid = len(self._data["inventory"][bead])/2
#    print mid, self.index2percent(bead, mid)
#    diff = 0
#    current = mid
#    allDone = 0
#    while(allDone <= 0):
#      #(self._data["inventory"][bead][current] == 0) or (allDone == 1)):
#      if (diff > 0):
#        diff = diff*-1
#      else:
#        diff = diff*-1+1
#      current = mid + diff
#      print "hi", current, diff
#      if (current < 0 or current == len(self._data["inventory"][bead])):
#        allDone = 2
#      elif (self._data["inventory"][bead][current] == 1):
#        allDone = 1
#
#        
#
#
