from CSCI6461_Project_classes import *
from CSCI6461_Project_data import *
from CSCI6461_Project_gui_memory import *

def readFromMemory(address, indirect=False):
  # gets the value stored in memory, updates MAR/MBR accordingly and returns the result
  # does not write to any registers besides MAR and MBR
  # handles indirection, but not IX field (effective address should've been calculated already)
  # [address] integer, the location from memory to read from
  # [direct] boolean, specifies if it is a direct access
  # return -(fault ID)-1 if fault occurs
  # return [content] integer, the value stored in the memory location
  if address > 2047 or address < 0:
    fault(3)
    return -4
  data['MAR'].value_set(address)
  content = data['memory'][address]
  data['MBR'].value_set(content)
  if indirect: # indirection
    address = content
    if address > 2047 or address < 0:
      fault(3)
      return -4
    data['MAR'].value_set(address)
    content = data['memory'][address]
    data['MBR'].value_set(content)
  return content

def writeToMemory(address, value, indirect, checkReserve=True):
  # writes the value to address in memory, updates MAR/MBR accordingly
  # does not write to any registers besides MAR and MBR
  # handles indirection, but not IX field (effective address should've been calculated already)
  # [address] integer, the location from memory to write to
  # [value] integer, the value to write to the memory
  # [indirect] boolean, specifies if it is a direct write
  # [checkReserve] boolean, whether write location should be checked
  #   (normally can't write to memory location 0-5)
  # returns -(fault ID)-1 if fault occurs
  # otherwise return 0
  
  # get the effective memory address into MAR, update MBR as needed
  if address > 2047 or address < 0:
    fault(3)
    return -4
  data['MAR'].value_set(address)
  if indirect: # indirection
    address = data['memory'][address]
    data['MBR'].value_set(address)
    if address > 2047 or address < 0:
      fault(3)
      return -4
    data['MAR'].value_set(address)
  # try to write the value to MBR and effective address in memory
  if checkReserve and address<6:
    fault(0)
    return -1
  data['MBR'].value_set(value)
  data['memory'][address] = value
  memoryPageUpdate()
  return 0
  
def fault(id):
  # report a machine fault, then does the 
  # [id] integer range [0,3], for the kind of machine fault
  data['MFR'].value_set(2 ** id)
  address = data['PC'].value()
  writeToMemory(4, address, checkReserve=False, indirect=False)
  address = readFromMemory(1)
  data['PC'].value_set(address)
  
def HLT():
  # stops the machine by setting HALT register to 1
  data['HALT'].value_set(1)
  
def splitInstructionLoadStore(instruction):
  # [instruction] 16-bit integer (0-65535)
  # splits into opcode(6), r(2), ix(2), i(1), address(5) in that order
  # for load/store instructions below
  opcode = int(instruction/1024)
  r = int(instruction%1024/256)
  ix = int(instruction%256/64)
  i = int(instruction%64/32)
  address = instruction%32
  return opcode,r,ix,i,address
  
def LoadStoreInstExec(instruction):
  # execute load/store instructions (LDR/LDA/LDX/STR/STX)
  # [instruction] 16-bit integer
  # returns read value if instruction is a successful load
  # returns 0 if instruction is a successful write
  # returns -(fault ID)-1 if fault occurs
  opcode,r,ix,i,address = splitInstructionLoadStore(instruction)
  EA,value = address,0 # initialize effective address (EA) and return value
  if opcode in [1,2,3] and ix > 0:
    # Need to Calculate Effective Address
    EA = address + data["IXR"][ix].value()
  if opcode in [1,3,33]: # LD instructions (LDR/LDA/LDX)
    if opcode in [1,33]: # LDR/LDX
      # Get Value From Memory
      value = readFromMemory(EA, indirect=i)
    if opcode == 3: # LDA
      if i: # indirect LDA is equivalent to direct LDR
        value = readFromMemory(EA, False)
      else:
        value = EA
    if opcode in [1,3]: # LDR/LDA
      # load value into GPR
      data["GPR"][r].value_set(value)
    if opcode == 33 and ix>0: # LDX
      # load value into IXR
      data["IXR"][ix].value_set(value)
  elif opcode in [2,34]: # ST instructions (STR/STX)
    if opcode == 2: # STR
      # get value from GPR
      value = data["GPR"][r].value()
    if opcode == 34: # STX
      if ix>0:
        # get value from IXR
        value = data["IXR"][ix].value()
      else:
        # invalid IXR, 0 used
        value = 0
    value = writeToMemory(EA, value, indirect=i)
  return value

def execute(instruction):
  # execute instruction num
  # [instruction] 16-bit integer (0-65535)
  # returns True if executed normally
  # returns False if halted or faulted
    
  # gets opcode
  opcode = int(instruction/1024)
  if opcode == 0:
    HLT()
    return False
  elif opcode in [1,2,3,33,34]:
    return LoadStoreInstExec(instruction) >= 0
  else:
    fault(2)
    return False

def singleStep():
  # tries to run a single step
  # check if machine is stopped
  if data['HALT'].value() > 0:
    return
  # get instruction and check if it should execute
  address = data['PC'].value()
  instruction = readFromMemory(address)
  if instruction < 0:
    return # a fault occured, don't execute
  # update IR and execute
  data['IR'].value_set(instruction)
  status = execute(instruction)
  if not status:
    return # fault occured or halted, exit
  # finishing touches
  address += 1
  data['PC'].value_set(address)
  
def multiStep():
  # "run", keeps calling singleStep until stopped
  while data['HALT'].value() == 0:
    singleStep()