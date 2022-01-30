import tkinter
from tkinter import ttk, filedialog
from CSCI6461_Project_classes import *

def windowMemory_onClose(localVar):
  # trigger function when memory editor is closed
  if 'windowMemory' in localVar:
    # destroy and remove record of the window
    localVar['windowMemory'].destroy()
    del localVar['windowMemory']
  if 'openGUIMemory' in localVar:
    # reenable the button in optionsFrame for reopening editor
    localVar['openGUIMemory'].config(state=tkinter.NORMAL)

def memoryWrite(localVar, address):
  # trigger function when memory editor edits memory value
  # do nothing if memory editor isn't open
  if not 'windowMemory' in localVar:
    return
  # write the line in memory editor into memory
  localVar['memory'][address] = localVar['memoryEntry'][address%16].value()
  
def memoryPageUpdate(localVar):
  # trigger function when memory editor page number changes
  # do nothing if memory editor isn't open
  if not 'windowMemory' in localVar:
    return
  # get new page number
  memoryPageNum = int(localVar['memoryPageNum'].value() / 16)
  memoryEntry = localVar['memoryEntry'] # get the list of labeledBitString
  memory = localVar['memory'] # get reference to memory
  for i in range(16):
    address = memoryPageNum * 16 + i # calculate full address
    # change label text to reflect new memory address of entry
    memoryEntry[i].text_set(text="Word "+str(i)+" ("+hex(address)+"):")
    # update trigger function to write to the correct new memory address
    memoryEntry[i].trigs["memory_write"] = lambda: memoryWrite(localVar, address)
    # set the entry to the true value of the memory
    memoryEntry[i].value_set(memory[address], trigger=False)
    
def programLoad(localVar):
  fileName = filedialog.askopenfilename(title="Select File", initialdir=".")
  if len(fileName) > 0:
    content = open(fileName,"r").read().splitlines()
    localVar['memory'] = memory = [0]*2048
    for i in range(len(content)):
      line = content[i].split()
      if len(line) != 2:
        print("Error loading: line "+str(i+1)+" has "+str(len(line)) \
          +" terms when it is supposed to have 2, skipping.")
        continue
      addr,val = 0,0
      try:
        addr,val = int(line[0],16),int(line[1],16)
      except:
        print("Error loading: line "+str(i+1) \
          +"'s content does not appear to be hexadecimal, skipping.")
        continue
      if addr > 2047 or addr < 0:
        print("Error loading: line "+str(i+1) \
          +"'s address is out of bounds [0,2047], skipping.")
        continue
      if val > 65535 or val < 0:
        print("Error loading: line "+str(i+1) \
          +"'s value is out of bounds [0,65535], skipping.")
        continue
      memory[addr] = val
    memoryPageUpdate(localVar)

def guiMemory(localVar):
  # start making interface for memory view/configuration
  # disable the open window button to prevent opening it again
  # windowMemory
  # ├memoryPage
  # │└memoryPageNum
  # └memoryCont
  #  └memoryEntry[0,15]
  
  if 'openGUIMemory' in localVar:
    localVar['openGUIMemory'].config(state=tkinter.DISABLED)
  # create a separate window to view/edit the memory
  localVar['windowMemory'] = windowMemory = tkinter.Tk() # create the window
  windowMemory.title("CSCI6461 Project Machine Memory") # name the window
  # if window is closed, destroy it
  windowMemory.protocol("WM_DELETE_WINDOW", lambda: windowMemory_onClose(localVar))
  # change disabled buttons to regular (black) text
  style = ttk.Style(master=windowMemory) # get style settings for windowMemory
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])

  # create a page number navigator, only top padding is needed
  memoryPage = ttk.Frame(windowMemory, padding=(0,10,0,0))
  memoryPage.grid(column=0,row=0)
  localVar['memoryPageNum'] = memoryPageNum = labeledBitString(12) \
    .create(frame=memoryPage, text="Memory Address: ", gap=4)
  # disable some buttons because they don't correspond to valid page numbers
  for i in [0,8,9,10,11]:
    memoryPageNum.bits[i].btn.config(state=tkinter.DISABLED)
  
  # create main body of memory editor
  memoryCont = ttk.Frame(windowMemory, padding=10)
  memoryCont.grid(column=0,row=1)
  localVar['memoryEntry'] = memoryEntry = [0]*16
  for i in range(16):
    memoryEntry[i] = labeledBitString(16).create(frame=memoryCont, y=i, width=14)
    
  # add number navigator trigger and call once
  memoryPageNum.trigs["page_update"] = lambda: memoryPageUpdate(localVar)
  memoryPageUpdate(localVar)
  