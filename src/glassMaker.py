#!/usr/bin/env python

import recipe as R
import glass as G
import cmd, sys

beads = []
recipe = R.Recipe()

class Shell(cmd.Cmd):
  intro = 'Welcome to the glass maker shell. Type help or ? to list commands.\n'
  prompt = 'gm>'
  file = None

  # ----- commands -----
  def do_makeBead(self, arg):
    'Make a new bead with list of elements and moles: e.g., Al 2 O 10:'
    argp=parse(arg)
    beads.append(G.Glass())
    #print argp
    for i in range(len(argp)/2):
      element = argp[2*i]
      mols = int(argp[2*i+1])
      beads[-1].addElement(element, mols)

  def do_setTarget(self, arg):
    'Set target percentages for element in new bead: e.g., "Al 0 8 12 1" sets target element "AL" in bead 0 (initialized with makeBead) from 8% to 12%, in 1% increments'
    argp=parse(arg)
    beadIndex = int(argp[1])
    element = argp[0]
    percentMin = float(argp[2])
    percentMax = float(argp[3])
    percentInc = float(argp[4])
    recipe.addElementWithBeadInRange(beads[beadIndex], element, percentMin, percentMax, percentInc)
    
  def do_initInventory(self, arg):
    'Initialize inventory of target beads (defaul: no inventory)'
    recipe.initInventory()

  def do_suggestNext(self, arg):
    'Suggest next bead combination'
    recipe.suggestNext()

  def do_addInventory(self, arg):
    'Add bead combination to inventory: e.g., "addInventory 8 3" adds the target with 8% of first element and 3% of second'
    argp=parse(arg)
    per0 = float(argp[0])
    per1 = float(argp[1])
    recipe.addInventory(per0, per1)
   
  def do_writeJSON(self, arg):
    'Write JSON save file(s)'
    print parse(arg)[0]
    recipe.writeJSON(parse(arg)[0])
  
  def do_quit(self, arg):
    'Stop recording, close and exit:  QUIT'
    self.close()
    return True

  def do_exit(self, arg):
    'Stop recording, close and exit:  EXIT'
    return self.do_quit(arg)

  # ----- record and playback -----
  def do_record(self, arg):
    'Save future commands to filename:  RECORD recipe.cmd'
    self.file = open(arg, 'w')
  def do_playback(self, arg):
    'Playback commands from a file:  PLAYBACK recipe.cmd'
    self.close()
    with open(arg) as f:
      self.cmdqueue.extend(f.read().splitlines())
  def precmd(self, line):
    #line = line.lower()
    if self.file and 'playback' not in line:
      print >>self.file, line
      #print(line, file=self.file)
    return line
  def close(self):
    if self.file:
      self.file.close()
      self.file = None

def parse(arg):
  'Convert a series of zero or more numbers to an argument tuple'
  return tuple(map(str, arg.split()))

if __name__ == '__main__':
    Shell().cmdloop()
