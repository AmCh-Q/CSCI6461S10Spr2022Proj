import tkinter
from tkinter import ttk
from CSCI6461_Project_classes import *
from CSCI6461_Project_data import *

def windowMemory_onClose():
  # trigger function when memory editor is closed
  if 'windowMemory' in data:
    # destroy and remove record of the window
    data['windowMemory'].destroy()
    del data['windowMemory']
  if 'guiMemoryBtn' in data:
    # re-enable the button in optionsFrame for reopening editor
    data['guiMemoryBtn'].config(state=tkinter.NORMAL)

def memoryWriteTrig(address):
  # trigger function when memory editor edits memory value
  # do nothing if memory editor isn't open
  from CSCI6461_Project_gui_cache import cacheLineUpdate
  if not 'windowMemory' in data:
    return
  blockNum = address//16
  wordNum = address%16
  # write the line in memory editor into memory
  data['memory'][address] = data['memoryEntry'][wordNum].value()
  # disable any cache line for this memory address
  for i in range(16):
    if data['cache'][i][17] == 1 and data['cache'][i][16] == blockNum:
      # if tag matches and is initialized, disable by setting initialization bit to 0
      data['cache'][i][17] = 0
  cacheLineUpdate()
  
def memoryBlockUpdate():
  # trigger function when memory editor block number changes
  # do nothing if memory editor isn't open
  if not 'windowMemory' in data:
    return
  # get new block number
  memoryBlockNum = (data['memoryBlockNum'].value() >> 4)
  data['memoryBlockNum'].labelTxt.config(text=f"Memory Address (Block {memoryBlockNum}): ")
  memoryEntry = data['memoryEntry'] # get the list of labeledBitString
  memory = data['memory'] # get reference to memory  
  for i in range(16):
    address = memoryBlockNum * 16 + i # calculate full address
    # change label text to reflect new memory address of entry
    memoryEntry[i].text_set(text=f"Word {str(i)} ({address:#0{5}X}):".replace("X","x"))
    # update trigger function to write to the correct new memory address
    #   python default param hackery involved: https://tinyurl.com/2d7bdwp6
    memoryEntry[i].trigs["memory_write"] = lambda a=address: memoryWriteTrig(a)
    # set the entry to the true value of the memory
    memoryEntry[i].value_set(memory[address], trigger=False)

def guiMemoryJump(blockNum):
  if not 'windowMemory' in data:
    guiMemory()
  else:
    data['windowMemory'].after(1, lambda: data['windowMemory'].focus_force())
  data['memoryBlockNum'].value_set(blockNum*16)

def guiMemory():
  # start making interface for memory view/configuration
  # GUI Structure:
  # windowMemory
  # ├memoryBlockFrame
  # │└memoryBlockNum
  # └memoryContFrame
  #  └memoryEntry[0,15]
  
  # disable the open window button to prevent opening it again
  if 'guiMemoryBtn' in data:
    data['guiMemoryBtn'].config(state=tkinter.DISABLED)
  # create a separate window to view/edit the memory
  data['windowMemory'] = windowMemory = tkinter.Tk() # create the window
  windowMemory.title("CSCI6461 Project Machine Memory") # name the window
  # if window is closed, destroy it
  windowMemory.protocol("WM_DELETE_WINDOW", windowMemory_onClose)
  # change disabled buttons to regular (black) text, label font to monospace
  style = ttk.Style(master=windowMemory) # get style settings for windowMemory
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])
  style.configure("Courier.TLabel", font=('Courier', 12))

  # create a block number navigator, only top padding is needed
  memoryBlockFrame = ttk.Frame(windowMemory, padding=(0,10,0,0))
  memoryBlockFrame.grid(column=0,row=0)
  data['memoryBlockNum'] = memoryBlockNum = labeledBitString(12) \
    .create(frame=memoryBlockFrame, text="Memory Address (Block 0): ", width=26)
  # disable some buttons because they don't correspond to valid block numbers
  for i in [0,8,9,10,11]:
    memoryBlockNum.bits[i].btn.config(state=tkinter.DISABLED)
  
  # create main body of memory editor
  memoryContFrame = ttk.Frame(windowMemory, padding=10)
  memoryContFrame.grid(column=0,row=1)
  data['memoryEntry'] = memoryEntry = [0]*16
  for i in range(16):
    memoryEntry[i] = labeledBitString(16).create(frame=memoryContFrame, y=i, width=15)
    
  # add block number navigator trigger and call once
  memoryBlockNum.trigs["block_num_update"] = memoryBlockUpdate
  memoryBlockUpdate()

  # show the window, for use with PyCharm
  # see https://stackoverflow.com/questions/51253078/tkinter-isnt-working-with-pycharm/51261747
  # windowMemory.mainloop()
