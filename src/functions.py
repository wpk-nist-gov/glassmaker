# utility functions

def findInList(value, searchList):
  """ If value is in searchList, return [True, index]
  where searchList[index] == value.
  Otherwise, return [False, -1] """
  for index in range(0, len(searchList)):
    if (searchList[index] == value):
      return True, index
  return False, -1

def unitConvert(listPair, units):
  """ Given a list pair as [value, "units"], convert to "units" and return new list pair """
  if ( (type(listPair) != list) or (len(listPair) != 2) ):
    raise RuntimeError("listPair must be given in the form [value, \"units\"]")
  if ( type(units) != str):
    raise RuntimeError("new units must be given as str")
  unitOld = _unitFac(listPair[1])
  unitNew = _unitFac(units)
  if ( unitOld[1] != unitNew[1] ):
    raise RuntimeError("unit types cannot be converted")
  return [listPair[0]*unitNew[0]/unitOld[0], units]

def _unitFac(units):
  """ given units, return the unit factor and unit type as follows
  mass:   g (grams) is base 1 """
  if (units == "g"):
    fac = 1
    utype = "mass"
  elif (units == "kg"):
    fac = 1e-3
    utype = "mass"
  else:
    raise RuntimeError("unrecognized units")
  return fac, utype

  
  

