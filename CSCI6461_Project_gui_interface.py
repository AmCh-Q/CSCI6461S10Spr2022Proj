import sys,tkinter
from tkinter import ttk
from CSCI6461_Project_classes import *
from CSCI6461_Project_gui_memory import *
from CSCI6461_Project_gui_cache import *
from CSCI6461_Project_execution import *
from CSCI6461_Project_data import *

def guiInterface():
  # start making all the interface related stuffs
  # we have widgets placed in a frame, and frames places in a window
  # position is defined in x(column) and y(row)
  # x=0,y=0 is the top left, going right/down is the positive x/y direction
  # GUI structure:
  # windowInterface
  # ├registersGPRFrame
  # │└GPR[0,3],IXR[1,3]
  # └controlsFrame
  #  ├registersMainFrame
  #  │└PC,MAR,MBR,IR
  #  ├conditionsFrame
  #  │└MFR,CC,HLT
  #  └optionsFrame
  #   └Step,Run,Store,St+,Load,Initialize,Memory
  
  data['windowInterface'] = windowInterface = tkinter.Tk() # create the GUI window
  windowInterface.title("CSCI6461 Project Machine Interface") # name the window
  # add trigger: if window is closed, call sys.exit() to end the program
  windowInterface.protocol("WM_DELETE_WINDOW", sys.exit)
  
  # the original ttk style for disabled buttons have gray text, which is hard to read
  #   so change it to regular (black) text
  # also change label font to monospace for easier reading and managing layouts
  style = ttk.Style(master=windowInterface) # get style settings for windowInterface
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])
  style.configure("Courier.TLabel", font=('Courier', 12))
  
  # create a frame to fit GPR and IXR
  data['registersGPRFrame'] = registersGPRFrame = ttk.Frame(windowInterface, padding=10)
  registersGPRFrame.grid(column=0,row=0) # place the frame
  data['GPR'],data['IXR'] = GPR,IXR = [None]*4,[None]*4 # initialize list for the registers
  for i in range(4): # create all 4 GPR registers
    GPR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text=f"GPR {str(i)}:", x=0, y=i, gap=0, width=6)
  for i in range(1,4): # create all 3 IXR registers
    IXR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text=f"IXR {str(i)}:", x=0, y=i+4, gap=0, width=6)
  # create a small spacer between GPR and IXR, just to make things look better
  spacerGPR = ttk.Label(registersGPRFrame, text="")
  spacerGPR.grid(column=0,row=4)

  # create frame besides registersGPRFrame, no left padding
  data['controlsFrame'] = controlsFrame = ttk.Frame(windowInterface, padding=(0,10,10,10))
  controlsFrame.grid(column=1,row=0) # place the frame
  
  # create a frame inside controlsFrame to fit first batch of registers
  data['registersMainFrame'] = registersMainFrame = ttk.Frame(controlsFrame)
  registersMainFrame.grid(column=0,row=0) # place the frame
  # create each row of the registers by calling class methods above
  #   for what each of these parameters do, read the definition in CSCI6461_Project_classes
  data['PC'] = labeledBitString(12).create(frame=registersMainFrame, text="PC:", x=0, y=0, gap=4)
  data['MAR'] = labeledBitString(12).create(frame=registersMainFrame, text="MAR:", x=0, y=1, gap=4)
  data['MBR'] = labeledBitString(16).create(frame=registersMainFrame, text="MBR:", x=0, y=2, gap=0)
  data['IR'] = labeledBitString(16).create(frame=registersMainFrame, text="IR:", x=0, y=3, gap=0)
  
  # create a frame inside controlsFrame to fit the condition registers
  data['conditionsFrame'] = conditionsFrame = ttk.Frame(controlsFrame)
  conditionsFrame.grid(column=0,row=2) # place the frame
  data['MFR'] = labeledBitString(4).create(
    frame=conditionsFrame, text="MFR:", x=0, numLabels=False)
  data['CC'] = labeledBitString(4).create(
    frame=conditionsFrame, text="CC:", x=6, numLabels=False)
  data['HALT'] = labeledBitString(1).create(
    frame=conditionsFrame, text="HALT:", x=12, numLabels=False)
  data['RUN'] = labeledBitString(1).create(
    frame=conditionsFrame, text="RUN:", x=15, numLabels=False)
  
  # create small spacers among condition registers
  # and between condition registers and mainRegs/buttons, just to make things look better
  spacerConditions1 = ttk.Label(conditionsFrame, text="", width=3)
  spacerConditions1.grid(column=5,row=0)
  spacerConditions2 = ttk.Label(conditionsFrame, text="", width=3)
  spacerConditions2.grid(column=11,row=0)
  spacerConditions3 = ttk.Label(conditionsFrame, text="", width=3)
  spacerConditions3.grid(column=14,row=0)
  spacerMains = ttk.Label(controlsFrame, text="")
  spacerMains.grid(column=0,row=1)
  spacerControls = ttk.Label(controlsFrame, text="")
  spacerControls.grid(column=0,row=3)
  
  # create a frame inside controlsFrame to fit all the command buttons
  data["optionsFrame"] = optionsFrame = ttk.Frame(controlsFrame)
  optionsFrame.grid(column=0,row=4)
  # button for single stepping execution
  data['singleStepBtn'] = singleStepBtn = ttk.Button( \
    optionsFrame, text="Step", width = 8, command=singleStep)
  singleStepBtn.grid(column=0,row=0)
  # button for continuous execution
  data['runBtn'] = runBtn = ttk.Button( \
    optionsFrame, text="Run", width = 8, command=multiStep)
  runBtn.grid(column=1,row=0)
  # button for store button
  data['storeBtn'] = storeBtn = ttk.Button( \
    optionsFrame, text="Store", width = 8, command=lambda: store(plus=False))
  storeBtn.grid(column=3,row=0)
  # button for st+ button
  data['storePlusBtn'] = storePlusBtn = ttk.Button( \
    optionsFrame, text="St+", width = 8, command=lambda: store(plus=True))
  storePlusBtn.grid(column=4,row=0)
  # button for load button
  data['loadBtn'] = loadBtn = ttk.Button( \
    optionsFrame, text="Load", width = 8, command=lambda: readFromMemory(data['MAR'].value(), indirect=False))
  loadBtn.grid(column=5,row=0)
  # button for opening Loading Memory
  data['programLoadBtn'] = programLoadBtn = ttk.Button( \
    optionsFrame, text="Initialize", width = 8, command=programLoad)
  programLoadBtn.grid(column=7,row=0)
  # button for opening Memory Editor
  data['guiMemoryBtn'] = guiMemoryBtn = ttk.Button( \
    optionsFrame, text="Memory", width = 8, command=guiMemory)
  guiMemoryBtn.grid(column=8,row=0)
  # button for opening Cache Editor
  data['guiCacheBtn'] = guiCacheBtn = ttk.Button( \
    optionsFrame, text="Cache", width = 8, command=guiCache)
  guiCacheBtn.grid(column=9,row=0)
  
  # create small spacers between some buttons
  spacerRun = ttk.Label(optionsFrame, text="", width=2)
  spacerRun.grid(column=2, row=0)
  spacerLoad = ttk.Label(optionsFrame, text="", width=2)
  spacerLoad.grid(column=6, row=0)

  # show the window, for use with PyCharm
  # see https://stackoverflow.com/questions/51253078/tkinter-isnt-working-with-pycharm/51261747
  # windowInterface.mainloop()
  
def store(plus=False):
  # a function to be called for store and st+ button clicks
  # [plus] boolean, whether it is a st+ function
  address = data['MAR'].value()
  value = data['MBR'].value()
  writeToMemory(address, value, checkReserve=False, indirect=False)
  if plus:
    data['MAR'].value_set(address+1)
