# glass - glass maker

import periodictable as PT
import functions as F
import os
import json
import copy

# NOTE: reorganize this data structure?? - { "elements" : { "C" : { "name" : carbon, "mols" : 1, "MW" : 12.0107 } } }

# NOTE: How to handle isotopes?? (check periodictable documentation)

class Glass(object):
  def __init__(self):
    """Return a new object to represent a glass bead
    The glass is described by a structured data format
    Each element possess:
      name:   name of element
      mols:   number of mols
      MW:     molecular weight """
    self._data = { "elements" : { "name" : [], "mols" : [], "MW" : [] } }
 
  def _checkSizes(self):
    nameLen = len(self._data["elements"]["name"])
    molsLen = len(self._data["elements"]["mols"])
    MWLen   = len(self._data["elements"]["MW"])
    if ( (nameLen != molsLen) or (nameLen != MWLen) or (molsLen != MWLen) ):
      raise RuntimeError("checkSize failed")

  def nElements(self):
    """ Return number of elements """
    return len(self._data["elements"]["name"])
  
  def addElement(self, elementName, elementMols):
    """Add an element to the glass"""
    
    # raise exceptions
    if (elementMols <= 0):
      raise RuntimeError("elementMols must be positive")
    atoms = PT.formula(elementName).atoms
    if (len(atoms) != 1):
      raise RuntimeError("elementName must have only one atom")
    for i in atoms:
      if (atoms[i] != 1):
        raise RuntimeError("elementName must have only one atom")
    
    # determine if added element is new or already exists
    nameList = self._data["elements"]["name"]
    inList,index = F.findInList(elementName, nameList)
    if (inList):
      self._data["elements"]["mols"][index] += elementMols
    else:
      molecularWeight = PT.elements.symbol(elementName).mass
      self._data["elements"]["name"].append(elementName)
      self._data["elements"]["mols"].append(float(elementMols))
      self._data["elements"]["MW"].append(molecularWeight)
    self._checkSizes()
  
  def writeJSON(self, fileName):
    """ write glass object to JSON file"""
    if (os.path.isfile(fileName+".json")):
      print "Warning: backing-up \""+fileName+".json\" to \""+fileName+".json.bak\""
      os.rename(fileName+".json", fileName+".json.bak")
    with open(fileName+".json", 'w') as f:
      json.dump(self._data, f)

  def readJSON(self, fileName):
    """ read glass object from JSON file"""
    with open(fileName+".json", 'r') as f:
      self._data = json.load(f)
    self._checkSizes()

  def totalMass(self):
    """ Return total mass as a list, [ value, "units" ] """
    mass = 0
    molList = self._data["elements"]["mols"]
    MWList = self._data["elements"]["MW"]
    for el in range(0, len(molList)):
      mass += molList[el] * MWList[el]
    return [mass, "g"]
  
  def _dataIndex(self, index):
    """ Return dataIndex (integer for index of _data)
    index can either be integer index for _data (fast)
    or string with atomic symbol (slow, order(len(_data))) """
    if ( type(index) == int):
      dataIndex = index
    elif ( type(index) == str):
      inList,dataIndex = F.findInList(index, self._data["elements"]["name"])
      if (not inList):
        raise RuntimeError("element is not present")
    else:
      raise RuntimeError("requires integer or string argument")
    return dataIndex

  def mass(self, index):
    """ Return mass of index(int or str) """
    dataIndex = self._dataIndex(index)
    mass = (self._data["elements"]["mols"][dataIndex] *  
            self._data["elements"]["MW"][dataIndex])
    return [mass, "g"]

  def massFraction(self, index):
    """ Return mass fraction of index """ 
    return self.mass(index)[0]/self.totalMass()[0]

  def totalMols(self):
    """ Return total moles """
    mols = 0
    MWList = self._data["elements"]["MW"]
    for iMols in self._data["elements"]["mols"]:
      mols += iMols
    return mols
  
  def mols(self, index):
    """ Return mols of index(int or str) """
    dataIndex = self._dataIndex(index)
    return self._data["elements"]["mols"][dataIndex]

  def molFraction(self, index):
    """ Return mass fraction of index """ 
    return self.mols(index)/self.totalMols()

  def meld(self, glass):
    """ Return the combination of two glasses """
    # perform a deep copy of self, then add glass
    newGlass = copy.deepcopy(self)
    for i in range(0, glass.nElements()):
      newGlass.addElement(glass._data["elements"]["name"][i],
                          glass._data["elements"]["mols"][i])
    return newGlass



