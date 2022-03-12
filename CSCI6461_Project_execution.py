import tkinter
from tkinter import ttk
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
    
def splitInstuctionShift(instruction):
  # [instruction] 16-bit integer (0-65535)
  # splits into opcode(6),r(2),al(1),lr(1),unused(2),count(4) in that order
  # for arithmetic and logical instructions
  # the unused(2) bits are ignored
  opcode = instruction >> 10
  r = (instruction >> 8) & 0b11
  al = (instruction >> 7) & 0b1
  lr = (instruction >> 6) & 0b1
  count = instruction & 0b1111
  return opcode,r,al,lr,count
  
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
    
  if value >= (1 << 15) or value < (-1 << 15): # value overflowed, set cc(0) to 1
    cc = 0b1000 # using bitwise OR to to set cc(0)
    
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
    
def ArithmeticInstExec(instruction):
  # execute Multiplication/Division instructions (MLT/DVD/TRR/AND/ORR/NOT)
  # [instruction] 16-bit integer
  opcode,rx,ry = splitInstuctionArithmetic(instruction)
  upperRes,lowerRes,cc=0,0,0
  rxValue = data["GPR"][rx].value()
  ryValue = data["GPR"][ry].value()
  
  if opcode == 18 and rxValue==ryValue: # TRR
    cc=0b0001 # equal
    
  if opcode == 17 and ryValue == 0:
    cc=0b0010 # Divide by 0
  elif opcode in [16,17]:
    if (rxValue >> 15) > 0:
      rxValue -= (1 << 16)
    if (ryValue >> 15) > 0:
      ryValue -= (1 << 16)
    if opcode == 16:  # MLT
      upperRes = (rxValue * ryValue) // (1 << 16)
      lowerRes = (rxValue * ryValue) % (1 << 16)
    elif opcode == 17: # DVD
      upperRes = rxValue // ryValue
      lowerRes = rxValue % ryValue
    if upperRes < 0:
      upperRes += (1 << 16)
    # store the two values in the two registers
    data["GPR"][rx].value_set(upperRes)
    data["GPR"][rx + 1].value_set(lowerRes)

  if opcode in [19,20,21]: # AND/ORR/NOT
    if opcode == 19:
      rxValue &= ryValue
    elif opcode == 20:
      rxValue |= ryValue
    elif opcode == 21:
      rxValue ^= (1<<16)-1
    data["GPR"][rx].value_set(rxValue)
  
  # Set and Return cc
  data["CC"].value_set(cc)
  return cc
  
def ShiftInstExec(instruction):
  # Execute Shift instructions (SRC/RRC)
  # [instruction] 16-bit integer
  opcode,r,al,lr,count = splitInstuctionShift(instruction)
  value = data["GPR"][r].value()
  cc,overflowPart,negative=0,0,False
  
  if al==0 and (value >> 15) > 0:
    # if arithmetic shift, and the sign bit is 1
    # it is considered as a negative number
    value %= 1 << 15
    negative = True
  if lr == 0: # Right shift
    bottomPart = value % (1<<count) # get the shifted away bits
    if opcode == 26: # RRC, shift bottomPart to correct place for overflowPart
      overflowPart = bottomPart << (15+al-count)
    else: # SRC
      if bottomPart > 0: # SRC underflowed
        cc = 0b0100
      if negative: # arithmetic shifting negative number, fill with 1s
        overflowPart = ((1<<count) - 1) << (15+al-count)
    value = value >> count
  else: # Left shift
    value = value << count
    topPart = value >> (15+al) # get the shifted away bits
    if opcode == 26: # RRC, set overflowPart
      overflowPart = topPart
    elif topPart > 0: # SRC overflowed
      cc = 0b1000
    value %= 1<<(15+al)
  value |= overflowPart
  if negative: # convert negative number back
    value |= 1<<15
    
  # Set and Return result and cc
  data["GPR"][r].value_set(value)
  data["CC"].value_set(cc)
  return cc

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
  elif opcode in range(4,8):
    return AddSubInstExec(instruction) >= 0
  elif opcode in range(8,16):
    return TransferInstExec(instruction) >= 0
  elif opcode in range(16,22):
    return ArithmeticInstExec(instruction) >= 0
  elif opcode in [25,26]:
    return ShiftInstExec(instruction) >=0
  elif opcode in [49,50,51]:
    return ioInstExec(instruction) >= 0
  else:
    fault(2)
    return False

def singleStepTrig():
  data['runBtn'].config(state=tkinter.DISABLED)
  data['singleStepBtn'].config(state=tkinter.DISABLED)
  singleStep()
  data['runBtn'].config(state=tkinter.NORMAL)
  data['singleStepBtn'].config(state=tkinter.NORMAL)

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
  
def multiStep(updateInterval=1,inverse=False):
  # "run", keeps calling singleStep until stopped
  # [updateInterval] integer > 0, how often would the interface update the displayed values
  # [inverse] boolean, whether the value of the run button should be taken as its inverse
  if not inverse and data['RUN'].value() == 0:
    data['RUN'].value_set(1,False)
  elif not inverse and data['RUN'].value() == 1:
    data['RUN'].value_set(0,False)
  # disable the step button, set RUN signal to 1
  data['singleStepBtn'].config(state=tkinter.DISABLED)
  updateStep = 0
  while data['HALT'].value() == 0 and data['RUN'].value() == 1:
    singleStep()
    if updateStep == 0:
      data['windowInterface'].update()
    updateStep = (updateStep+1)%updateInterval
  # re-enable the step button, set RUN signal to 0
  data['RUN'].value_set(0,False)
  data['singleStepBtn'].config(state=tkinter.NORMAL)
