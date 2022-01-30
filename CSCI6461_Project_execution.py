from CSCI6461_Project_classes import *

def execute(localVar, instruction):
  # trying to execute instruction num
  raise NotImplementedError 

def singleStep(localVar):
  address = localVar['PC'].value()
  if address > 2047 or address < 0:
    # handle case of memory out of bounds
    raise NotImplementedError
  instruction = localVar['memory'][address]
  localVar['IR'].value_set(instruction)
  execute(localVar, instruction)
  address += 1
  localVar['PC'].value_set(address)