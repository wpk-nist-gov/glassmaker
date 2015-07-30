#!/usr/bin/env python

import functions as F
import unittest

class TestFunctions(unittest.TestCase):
  def testFindInList(self):
    searchList = range(0, 5)
    self.assertEqual(False, F.findInList(0.5, searchList)[0])
    self.assertEqual(-1, F.findInList(0.5, searchList)[1])
    self.assertEqual(True, F.findInList(3, searchList)[0])
    self.assertEqual(3, F.findInList(3, searchList)[1])
    searchList = [0.5, 1.9]
    self.assertEqual(True, F.findInList(1.9, searchList)[0])
    self.assertEqual(1, F.findInList(1.9, searchList)[1])
    searchList = ["cats", "dogs"]
    self.assertEqual(False, F.findInList("cat", searchList)[0])
    self.assertEqual(-1, F.findInList("cat", searchList)[1])
    self.assertEqual(True, F.findInList("cats", searchList)[0])
    self.assertEqual(0, F.findInList("cats", searchList)[1])

  def testUnitConvert(self):
    self.assertEqual([0.01217, "kg"], F.unitConvert([12.17, "g"], "kg"))
    self.assertRaises(RuntimeError, F.unitConvert, [12.17, 13.0, "g"], "kg") 
    self.assertRaises(RuntimeError, F.unitConvert, 12.17, "kg") 

if __name__ == '__main__':
  unittest.main()

