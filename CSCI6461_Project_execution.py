from CSCI6461_Project_classes import *
from CSCI6461_Project_data import *

def execute(instruction):
  # trying to execute instruction num
  raise NotImplementedError 

def singleStep():
  address = data['PC'].value()
  if address > 2047 or address < 0:
    # handle case of memory out of bounds
    raise NotImplementedError
  instruction = data['memory'][address]
  data['IR'].value_set(instruction)
  execute(instruction)
  address += 1
  data['PC'].value_set(address)