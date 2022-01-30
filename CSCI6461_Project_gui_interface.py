import tkinter
from tkinter import ttk
from CSCI6461_Project_classes import *
from CSCI6461_Project_gui_memory import *
from CSCI6461_Project_execution import *

def guiInterface(localVar):
  # start making all the interface related stuffs
  # we have widgets placed in a frame, and frames places in a window
  # position is defined in x(column) and y(row)
  # x=0,y=0 is the top left, going right/down is the positive x/y direction
  # [localVar] if you want a local variable to be able to get accessed from outside
  # windowInterface
  # ├registersGPRFrame
  # │└GPR[0,3],IXR[1,3]
  # └controlsFrame
  #  ├registersMainFrame
  #  │└PC,MAR,MBR,IR,MFR,Priviledged
  #  └optionsFrame
  #   └openGUIMemory,programLoad
  
  localVar['windowInterface'] = windowInterface = tkinter.Tk() # create the GUI window
  windowInterface.title("CSCI6461 Project Machine Interface") # name the window
  # if window is closed, call quit() to end the program
  windowInterface.protocol("WM_DELETE_WINDOW", lambda: exec("quit()"))
  
  # the original ttk style for disabled buttons have gray text, which is hard to read
  #   so change it to regular (black) text
  style = ttk.Style(master=windowInterface) # get style settings for windowInterface
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])
  
  # create a frame to fit GPR and IXR
  localVar['registersGPRFrame'] = registersGPRFrame = ttk.Frame(windowInterface, padding=10)
  registersGPRFrame.grid(column=0,row=0) # place the frame
  localVar['GPR'],localVar['IXR'] = GPR,IXR = [None]*4,[None]*4 # initialize list for the registers
  for i in range(4): # create all 4 GPR registers
    GPR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text="GPR "+str(i)+":", x=0, y=i, gap=0, width=6)
  for i in range(1,4): # create all 3 IXR registers
    IXR[i] = labeledBitString(16) \
      .create(frame=registersGPRFrame, text="IXR "+str(i)+":", x=0, y=i+4, gap=0, width=6)
  # create a small spacer between GPR and IXR, just to make things look better
  spacerGPR = ttk.Label(registersGPRFrame, text="")
  spacerGPR.grid(column=0,row=4)

  # create frame besides registersGPRFrame, no left padding
  localVar['controlsFrame'] = controlsFrame = ttk.Frame(windowInterface, padding=(0,10,10,10))
  controlsFrame.grid(column=1,row=0) # place the frame
  
  # create a frame inside controlsFrame to fit first batch of registers
  localVar['registersMainFrame'] = registersMainFrame = ttk.Frame(controlsFrame)
  registersMainFrame.grid(column=0,row=0) # place the frame
  # create each row of the registers by calling class methods above
  #   for what each of these parameters do, read the definition in CSCI6461_Project_classes
  localVar['PC'] = labeledBitString(12).create(frame=registersMainFrame, text="PC:", x=0, y=0, gap=4)
  localVar['MAR'] = labeledBitString(12).create(frame=registersMainFrame, text="MAR:", x=0, y=1, gap=4)
  localVar['MBR'] = labeledBitString(16).create(frame=registersMainFrame, text="MBR:", x=0, y=2, gap=0)
  localVar['IR'] = labeledBitString(16).create(frame=registersMainFrame, text="IR:", x=0, y=3, gap=0)
  localVar['MFR'] = labeledBitString(4) \
    .create(frame=registersMainFrame, text="MFR:", x=0, y=4, gap=12, toggleAble=False)
  localVar['CC'] = labeledBitString(2) \
    .create(frame=registersMainFrame, text="CC:", x=0, y=5, gap=14, toggleAble=False)
  localVar['Priviledged'] = labeledBitString(1) \
    .create(frame=registersMainFrame, text="Priviledged: ", x=0, y=6, gap=15, toggleAble=False)
  
  # create a frame inside controlsFrame to fit all the command buttons
  localVar["optionsFrame"] = optionsFrame = ttk.Frame(controlsFrame)
  optionsFrame.grid(column=0,row=1)
  # button for single stepping execution
  localVar['singleStepBtn'] = singleStepBtn = ttk.Button( \
    optionsFrame, text="Single Step", command=lambda: singleStep(localVar))
  singleStepBtn.grid(column=0,row=0)
  # button for opening Memory Editor
  localVar['guiMemoryBtn'] = guiMemoryBtn = ttk.Button( \
    optionsFrame, text="Memory Editor", command=lambda: guiMemory(localVar))
  guiMemoryBtn.grid(column=1,row=0)
  # button for opening Loading Memory
  localVar['programLoadBtn'] = programLoadBtn = ttk.Button( \
    optionsFrame, text="ProgramLoad", command=lambda: programLoad(localVar))
  programLoadBtn.grid(column=2,row=0)
  