#!/usr/bin/env python

import glass as G
import unittest
from subprocess import call

class TestGlass(unittest.TestCase):
  def testAddElement(self):
    bead = G.Glass()
    
    # updates element names and mols
    self.assertEqual(0, bead.nElements())
    bead.addElement("C", 3)
    self.assertEqual(1, bead.nElements())
    self.assertEqual("C", bead._data["elements"]["name"][0])
    self.assertEqual(3, bead._data["elements"]["mols"][0])
    self.assertEqual(12.0107, bead._data["elements"]["MW"][0])
    bead.addElement("N", 3)
    self.assertEqual(2, bead.nElements())
    self.assertEqual("N", bead._data["elements"]["name"][1])
    self.assertEqual(3, bead._data["elements"]["mols"][1])
    self.assertEqual(14.0067, bead._data["elements"]["MW"][1])
    
    # adding mols of an existening element doesn't increase the number of unique elements
    bead.addElement("C", 1)
    self.assertEqual(2, bead.nElements())
    self.assertEqual(4, bead._data["elements"]["mols"][0])

    # exception is raised when attempting to add negative mols of an element
    #  note that arguments after "RuntimeError" are passed to bead.addElement
    self.assertRaises(RuntimeError, bead.addElement, "C", -1.5)  
    
    # exception is raised when attempting to add an element not recognized in periodic table
    self.assertRaises(ValueError, bead.addElement, "X", 1.5)  
    
    # exception is raised when attempting to add more than one element with addElement"""
    self.assertRaises(RuntimeError, bead.addElement, "CC", 1.5)  
    self.assertRaises(RuntimeError, bead.addElement, "C2", 1.5)  

  def testReadAndWriteJSON(self):
    bead = G.Glass()
    bead.addElement("C", 3)
    bead.addElement("N", 1)
    
    # test that bead.json is correctly written, can be read and data matches
    call(["mkdir", "-p","../test"])
    bead.writeJSON("../test/bead")
    bead2 = G.Glass()
    bead2.readJSON("../test/bead")
    self.assertEqual(bead.nElements(), bead2.nElements())
    self.assertEqual(bead._data, bead2._data)
    self.assertNotEqual(bead, bead2)
    bead.addElement("N", 1)
    self.assertNotEqual(bead._data, bead2._data)
    self.assertRaises(IOError, bead.readJSON, "/tmp/does/not/exist")

  def testMassAndMol(self):
    bead = G.Glass()
    bead.addElement("C", 3)
    bead.addElement("Al", 5)
    
    # test mass and mol functions
    self.assertAlmostEqual(134.90769, bead.mass("Al")[0], places=13)
    self.assertAlmostEqual("g", bead.mass("Al")[1], places=13)
    self.assertAlmostEqual(bead.mass("Al")[0], bead.mass(1)[0], places=13)
    self.assertRaises(RuntimeError, bead.mass, "X")
    self.assertRaises(RuntimeError, bead.mass, 1.0)
    self.assertRaises(IndexError, bead.mass, 120)
    self.assertAlmostEqual(0.7892117452583742, bead.massFraction("Al"), places=13)
    self.assertEqual(8, bead.totalMols())
    self.assertEqual(3, bead.mols("C"))
    self.assertEqual(bead.mols(0), bead.mols("C"))
    self.assertEqual(3./8., bead.molFraction("C"))
    self.assertAlmostEqual(170.93979, bead.totalMass()[0], places=13)
    self.assertEqual("g", bead.totalMass()[1])

  def testMeld(self):
    bead = G.Glass()
    bead.addElement("C", 3)
    bead.addElement("Al", 5)
    bead2 = G.Glass()
    bead2.addElement("Al", 1)
    bead2.addElement("N", 2)
    newBead = bead.meld(bead2)
    self.assertNotEqual(bead, newBead)
    self.assertNotEqual(bead2, newBead)
    self.assertNotEqual(bead, bead2)
    self.assertEqual(3, newBead.mols("C"))
    self.assertEqual(6, newBead.mols("Al"))
    self.assertEqual(2, newBead.mols("N"))

if __name__ == "__main__":
  unittest.main()



