from CSCI6461_Project_classes import *
from CSCI6461_Project_data import *
from CSCI6461_Project_gui_memory import *
from CSCI6461_Project_gui_cache import *
from CSCI6461_Project_gui_io import *
  
def fault(id):
  # report a machine fault, then does the 
  # [id] integer range [0,3], for the kind of machine fault
  data['MFR'].value_set(2 ** id)
  # store PC for machine fault to reserved location (at address 4)
  address = data['PC'].value()
  writeToMemory(4, address, checkReserve=False, indirect=False)
  # get the PC reserved for faults (at address 1)
  address = readFromMemory(1)
  data['PC'].value_set(address)
  
def HLT():
  # stops the machine by setting HALT register to 1
  data['HALT'].value_set(1)
  
def splitInstructionLoadStore(instruction):
  # [instruction] 16-bit integer (0-65535)
  # splits into opcode(6), r(2), ix(2), i(1), address(5) in that order
  # for load/store instructions below
  opcode = instruction >> 10
  r = (instruction >> 8) & 0b11
  ix = (instruction >> 6) & 0b11
  i = (instruction >> 5) & 0b1
  address = instruction & 0b11111
  return opcode,r,ix,i,address
  
def splitInstuctionArithmetic(instruction):
  # [instruction] 16-bit integer (0-65535)
  # splits into opcode(6), rx(2), ry(2) in that order
  # for arithmetic and logical instructions
  # the final 6 bits of the instruction are ignored
  opcode = instruction >> 10
  rx = (instruction >> 8) & 0b11
  ry = (instruction >> 6) & 0b11
  return opcode,rx,ry
  
def LoadStoreInstExec(instruction):
  # execute load/store instructions (LDR/LDA/LDX/STR/STX)
  # [instruction] 16-bit integer
  # returns read value if instruction is a successful load
  # returns 0 if instruction is a successful write
  # returns -(fault ID)-1 if fault occurs
  opcode,r,ix,i,EA = splitInstructionLoadStore(instruction)
  value = 0 # initialize return value
  if opcode in [1,2,3] and ix > 0:
    # Need to Calculate Effective Address
    EA += data["IXR"][ix].value()
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
  
def AddSubInstExec(instruction):
  # execute addition/subtraction instructions (AMR/SMR/AIR/SIR)
  # [instruction] 16-bit integer
  # calculate the value, sets cc accordingly, then returns the new value that's calculated
  # does not cause faults (always returns 0)
  opcode,r,ix,i,EA = splitInstructionLoadStore(instruction)
  value,cc = 0,0
  
  if opcode in [4,5]: # Add/Subtract from Memory (AMR/SMR)    
    if ix > 0: # Need to Calculate Effective Address with IXR
      EA += data["IXR"][ix].value()
    value = readFromMemory(EA, indirect=i)
  else: # opcode in [6,7] Add/Subtract Immediate (AIR/SIR)
    value = EA
  
  # if the sign bit is 1, it is considered as a negative number
  # change the value from EA and from GPR from unsigned to signed number
  if (value >> 15) > 0:
    value -= (1 << 16)
  gprvalue = data["GPR"][r].value()
  if (gprvalue >> 15) > 0:
    gprvalue -= (1 << 16)
    
  if opcode in [4,6]: # ADD insturction (AMR/AIR)
    value += gprvalue
  elif opcode in [5,7]: # SUB insturction (SMR/SIR)
    value = gprvalue - value
    
  if value >= (1 << 15): # value overflowed and is now a negative number, set cc(0) to 1
    cc |= 0b1000 # using bitwise OR to to set cc(0)
  elif value < (-1 << 15): # value underflowed and is now a positive number, set cc(1) to 1
    cc |= 0b0100 # using bitwise OR to to set cc(1)
    
  # using modulo to roll number back to unsigned [0,65535] then set GPR
  data["GPR"][r].value_set(value%(1<<16))
  # actually setting the cc register, then return
  data["CC"].value_set(cc)
  return 0
  
def TransferInstExec(instruction):
  # execute transfer instructions (JZ/JNE/JCC/JMA/JSR/RFS/SOB/JGE)
  # [instruction] 16-bit integer
  # set PC to EA if branching
  # returns 0 if not branching(PC unchanged)
  # returns -1 if branching(PC changed), to prevent incrementing PC
  opcode,r,ix,i,EA = splitInstructionLoadStore(instruction)
  jump = False
  
  if opcode == 13: # RFS
    data["GPR"][0].value_set(EA)
    # Branching, setting pc to R3
    pc = data["GPR"][3].value()
    data["PC"].value_set(pc)
    return -1
    
  if opcode in [8,9,14,15]: # need r (JZ/JNE/SOB/JGE)
    value = data["GPR"][r].value()
    if (value >> 15) > 0: # if the sign bit is 1, it is considered as a negative number
      value -= (1 << 16)
    elif opcode == 8: #JZ
      jump = (value == 0) # jump if zero
    elif opcode == 9: #JNE
      jump = (value != 0) # jump if nonzero
    elif opcode == 14: #SOB
      value -= 1
      data["GPR"][r].value_set(value % (1 << 16)) # may need to flip it back to positive
      jump = (value>0) # jump if positive after decrement
    elif opcode == 15: #JGE
      jump = (value>=0) # jump if non-negative
  if opcode == 10: # JCC
    cc = data["CC"].value()
    jump = ((cc & (0b1 << (3-ix))) > 0) # bitwise OR to get cc(ix), then check if it is >0
  if opcode in [11,12]: # JMA/JSR
    if opcode == 12: # JSR
      pc = data["PC"].value()
      data["GPR"][3].value_set(pc+1)
    jump = True
      
  if jump: # branching, setting PC to EA
    if ix > 0: # Need to Calculate Effective Address with IXR
      EA += data["IXR"][ix].value()
    if i>0: # indirection
      EA = readFromMemory(EA, indirect=False)
    data["PC"].value_set(EA)
    return -1
  else:
    return 0

def execute(instruction):
  # execute instruction num
  # [instruction] 16-bit integer (0-65535)
  # returns True if executed normally
  # returns False if halted or faulted or branched
    
  # gets opcode
  opcode = instruction >> 10
  if opcode == 0:
    HLT()
    return False
  elif opcode in [1,2,3,33,34]:
    return LoadStoreInstExec(instruction) >= 0
  elif opcode in [4,5,6,7]:
    return AddSubInstExec(instruction) >= 0
  elif opcode in [8,9,10,11,12,13,14,15]:
    return TransferInstExec(instruction) >= 0
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
    return # fault occured or halted or branched, exit
  # finishing touches
  address += 1
  data['PC'].value_set(address)
  
def multiStep(updateInterval=1):
  # "run", keeps calling singleStep until stopped
  windowInterface = data['windowInterface']
  data['RUN'].value_set(1)
  updateStep = 0
  while data['HALT'].value() == 0:
    singleStep()
    if updateStep == 0:
      windowInterface.update()
    updateStep = (updateStep+1)%updateInterval
  data['RUN'].value_set(0)
