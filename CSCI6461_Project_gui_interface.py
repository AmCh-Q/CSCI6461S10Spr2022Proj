import sys,tkinter
from tkinter import ttk, filedialog
from CSCI6461_Project_classes import *
from CSCI6461_Project_gui_memory import *
from CSCI6461_Project_gui_cache import *
from CSCI6461_Project_execution import *
from CSCI6461_Project_gui_io import *
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
  data['GPR'],data['IXR'],data['FR'] = GPR,IXR,FR = [None]*4,[None]*4,[None]*2 # initialize list for the registers
  for i in range(4): # create all 4 GPR registers
    GPR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text=f"GPR {str(i)}:", x=0, y=i, gap=0, width=6)
  for i in range(1,4): # create all 3 IXR registers
    IXR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text=f"IXR {str(i)}:", x=0, y=i+4, gap=0, width=6)
  for i in range(2): # create 2 FR registers
    FR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text=f"FR {str(i)}:", x=0, y=i+9, gap=0, width=6)
  # create a small spacer between GPR, IXR and FR, just to make things look better
  spacerGPR = ttk.Label(registersGPRFrame, text="")
  spacerGPR.grid(column=0,row=4)
  spacerIXR = ttk.Label(registersGPRFrame, text="")
  spacerIXR.grid(column=0,row=8)

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
  data['conditionsFrame'] = conditionsFrame = ttk.Frame(controlsFrame, padding=30)
  conditionsFrame.grid(column=0,row=2) # place the frame
  data['MFR'] = labeledBitString(4).create(
    frame=conditionsFrame, text="MFR:", x=0, numLabels=False)
  data['CC'] = labeledBitString(4).create(
    frame=conditionsFrame, text="CC:", x=6, padx=35, numLabels=False)
  data['HALT'] = labeledBitString(1).create(
    frame=conditionsFrame, text="HALT:", x=12, padx=35, numLabels=False)
  data['RUN'] = labeledBitString(1).create(
    frame=conditionsFrame, text="RUN:", x=15, padx=35, numLabels=False)
  data['RUN'].trigs["multiStep_trigger"] = lambda: multiStep(inverse=True)
  
  # create a frame inside controlsFrame to fit all the command buttons
  data["optionsFrame"] = optionsFrame = ttk.Frame(controlsFrame)
  optionsFrame.grid(column=0,row=4)
  # button for single stepping execution
  data['singleStepBtn'] = singleStepBtn = ttk.Button( \
    optionsFrame, text="Step", width = 8, command=singleStepTrig)
  singleStepBtn.grid(column=0,row=0,padx=15)
  # button for continuous execution
  data['runBtn'] = runBtn = ttk.Button( \
    optionsFrame, text="Run", width = 8, command=multiStep)
  runBtn.grid(column=0,row=1,padx=15)
  # button for store
  data['storeBtn'] = storeBtn = ttk.Button( \
    optionsFrame, text="Store", width = 8, command=lambda: store(plus=False))
  storeBtn.grid(column=1,row=0,padx=15)
  # button for st+
  data['storePlusBtn'] = storePlusBtn = ttk.Button( \
    optionsFrame, text="St+", width = 8, command=lambda: store(plus=True))
  storePlusBtn.grid(column=1,row=1,padx=15)
  # button for opening I/O Panel
  data['guiIoBtn'] = guiIoBtn = ttk.Button( \
    optionsFrame, text="I/O", width = 8, command=guiIo)
  guiIoBtn.grid(column=2,row=0,padx=15)
  # button for opening Loading Memory
  data['programLoadBtn'] = programLoadBtn = ttk.Button( \
    optionsFrame, text="Initialize", width = 8, command=programLoad)
  programLoadBtn.grid(column=3,row=0,padx=15)
  # button for load
  data['loadBtn'] = loadBtn = ttk.Button( \
    optionsFrame, text="Load", width = 8, command=lambda: readFromMemory(data['MAR'].value(), indirect=False))
  loadBtn.grid(column=3,row=1,padx=15)
  # button for opening Memory Editor
  data['guiMemoryBtn'] = guiMemoryBtn = ttk.Button( \
    optionsFrame, text="Memory", width = 8, command=guiMemory)
  guiMemoryBtn.grid(column=4,row=0,padx=15)
  # button for opening Cache Editor
  data['guiCacheBtn'] = guiCacheBtn = ttk.Button( \
    optionsFrame, text="Cache", width = 8, command=guiCache)
  guiCacheBtn.grid(column=4,row=1,padx=15)

  # show the window, for use with PyCharm
  # see https://stackoverflow.com/questions/51253078/tkinter-isnt-working-with-pycharm/51261747
  # windowInterface.mainloop()
    
def programLoad():
  # triggered when the Init button is clicked, tries to load a program
  # open file dialog to select file
  fileName = filedialog.askopenfilename(title="Select File", initialdir=".")
  # reset all registers, memory, cache to 0
  for i in range(4):
    data['GPR'][i].value_set(0)
  for i in range(1,4):
    data['IXR'][i].value_set(0)
  for i in range(2):
    data['FR'][i].value_set(0)
  for i in ['PC','MAR','MBR','IR','MFR','CC','HALT']:
    data[i].value_set(0)
  data['memory'] = memory = [0]*2048
  data['cache'] = [[0]*19 for i in range(16)]+[0]
  data['printText'] = ""
  data['inputText'] = ""
  # trigger update to io
  ioUpdate()
  data['memory'][1] = 6 # as suggested in project description, delete by phase 3
  # get content of file and write it into memory
  if len(fileName) > 0:
    content = []
    try:
      content = open(fileName,"r",encoding='utf-8').read().splitlines()
    except Exception as e:
      print(f"Error loading: file '{fileName}' does not appear to be a readable text file.")
      print(str(e))
      content = []
    for i in range(len(content)):
      line = content[i].split()
      if len(line) < 1:
        continue
      elif len(line) < 2:
        print(f"Warning: line {str(i+1)} has {str(len(line))}"\
          +" terms when it is supposed to have 2, skipping.")
        continue
      addr,val = 0,0
      try:
        addr,val = int(line[0],16),int(line[1],16)
      except Exception:
        print(f"Warning: line {str(i+1)}" \
          +"'s content does not appear to be hexadecimal, skipping.")
        continue
      if addr > 2047 or addr < 0:
        print(f"Warning: line {str(i+1)}'s address is out of bounds [0,2047], skipping.")
        continue
      elif val > 65535 or val < 0:
        print(f"Warning: line {str(i+1)}'s value is out of bounds [0,65535], skipping.")
        continue
      memory[addr] = val
  # trigger update to memories
  memoryBlockUpdate()
  # trigger update to cache
  cacheLineUpdate()
  
def store(plus=False):
  # a function to be called for store and st+ button clicks
  # [plus] boolean, whether it is a st+ function
  address = data['MAR'].value()
  value = data['MBR'].value()
  writeToMemory(address, value, checkReserve=False, indirect=False)
  if plus:
    data['MAR'].value_set(address+1)
