#!/usr/bin/env python

import recipe as R
import glass as G
import unittest
from subprocess import call

class TestRecipe(unittest.TestCase):
  def testAddEleANDreadWriteJSON(self):
    recipe = R.Recipe()
    bead1 = G.Glass()
    bead1.addElement("Al", 2)
    bead1.addElement("O", 10)
    bead2 = G.Glass()
    bead2.addElement("Ti", 2)
    bead2.addElement("O", 10)
    recipe.addElementWithBeadInRange(bead1, "Al", 8, 12, 1)  
    recipe.addElementWithBeadInRange(bead2, "Ti", 3, 6, 1)  
    recipe._checkSizes()
    recipe.writeJSON("../test/recipe")    
    recipe2 = R.Recipe()
    recipe2.readJSON("../test/recipe")
    recipe2.writeJSON("../test/recipe2")
    self.assertEqual(11, recipe.index2percent(0,3))
    self.assertEqual(2, recipe.percent2index(0,10))
    recipe.initInventory()
    recipe.suggestNext()
    recipe.addInventory(8, 3)
    recipe.suggestNext()
    recipe.addInventory(8, 5)
    recipe.suggestNext()
    recipe.addInventory(8, 4)
    recipe.suggestNext()
    recipe2.writeJSON("../test/recipe")

if __name__ == "__main__":
  unittest.main()
