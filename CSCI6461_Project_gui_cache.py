import tkinter
from tkinter import ttk
from CSCI6461_Project_classes import *
from CSCI6461_Project_data import *
from CSCI6461_Project_gui_memory import *

# cache structure:
# data['cache']
# ├data['cache'][lineNum] with lineNum in [0,15] for each cache line
# │├data['cache'][lineNum][wordNum] with wordNum in [0,15] for the 16-bit content of each word
# │├data['cache'][lineNum][16] is a 8-bit tag of the cache line
# │├data['cache'][lineNum][17] is the initialization bit of the cache line
# │└data['cache'][lineNum][18] is the dirty bit of the cache line
# └data['cache'][16] is an integer pointing to the cache line number to overwrite next

def windowCache_onClose():
  # trigger function when cache editor is closed
  if 'windowCache' in data:
    # destroy and remove record of the window
    data['windowCache'].destroy()
    del data['windowCache']
  if 'guiCacheBtn' in data:
    # re-enable the button in optionsFrame for reopening editor
    data['guiCacheBtn'].config(state=tkinter.NORMAL)
    
def cacheWriteTrig(lineNum, wordNum):
  # trigger function when cache editor edits cache value
  # do nothing if cache editor isn't open
  # [lineNum] integer, the cache line number to point to
  # [wordNum] integer, if in [0,15] will point to the corresponding cache word
  #   if [16,17,18] will point to tag, init bit, or dirty bit respectively
  if not 'windowCache' in data:
    return
  value = 0
  if wordNum < 16: # write the line in cache editor into cache
    value = data['cacheEntry'][wordNum].value()
  elif wordNum == 16: # write tag into cache
    value = data['cacheTag'].value()
  elif wordNum == 17: # write init bit into cache
    value = data['cacheInit'].value()
  elif wordNum == 18: # write dirty bit into cache
    value = data['cacheDirty'].value()
  data['cache'][lineNum][wordNum] = value
  if wordNum <= 16: # the content/tag of the cache is overwritten
    data['cacheDirty'].value_set(1)

def cacheLineUpdate():
  # trigger function when cache editor's cache line number changes
  # do nothing if cache editor isn't open
  if not 'windowCache' in data:
    return
  # get new line number
  cacheLineNum = data['cacheLineNum']
  lineNum = cacheLineNum.value()

  # update navigator label to new number
  cacheLineNum.labelTxt.config(text=f"Cache Line {lineNum}: ")
  
  cacheEntry = data['cacheEntry'] # get the list of labeledBitString
  cache = data['cache'] # get reference to cache  
  for i in range(16):    
    # update trigger function to write data to the correct new cache line
    #   python default param hackery involved: https://tinyurl.com/2d7bdwp6
    cacheEntry[i].trigs["cache_write"] = lambda a=lineNum, b=i: cacheWriteTrig(a,b)
    # set the entry to the true value of the cache
    cacheEntry[i].value_set(cache[lineNum][i], trigger=False)
  
  # update trigger function to write status to the correct new cache line
  #   python default param hackery involved: https://tinyurl.com/2d7bdwp6
  cacheTag = data['cacheTag']
  cacheTag.trigs["cache_write"] = lambda a=lineNum: cacheWriteTrig(a,16)
  cacheTag.value_set(cache[lineNum][16], trigger=False)
  cacheInit = data['cacheInit']
  cacheInit.trigs["cache_write"] = lambda a=lineNum: cacheWriteTrig(a,17)
  cacheInit.value_set(cache[lineNum][17], trigger=False)
  cacheDirty = data['cacheDirty']
  cacheDirty.trigs["cache_write"] = lambda a=lineNum: cacheWriteTrig(a,18)
  cacheDirty.value_set(cache[lineNum][18], trigger=False)
  
  # update destination when the guiMemoryJumpBtn is triggered to new line number
  data['guiMemoryJumpBtn'].config(command=lambda a=lineNum: guiMemoryJump(a))

def cache_next_update():
  # trigger function when cache editor's next replacement cache line number changes
  # do nothing if cache editor isn't open
  if not 'windowCache' in data:
    return
  data['cache'][16] = data['cacheNextNum'].value()

def guiCache():
  # start making interface for cache view/configuration
  # disable the open window button to prevent opening it again
  # GUI Structure:
  # windowCache
  # ├cacheLineFrame
  # │├cacheLineNum
  # │└cacheNextNum
  # ├cacheUtilFrame
  # │├guiMemoryJumpBtn
  # │└autoShowCacheBtn
  # ├cachePropertyFrame
  # │├cacheInit
  # │├cacheDirty
  # │└cacheTag
  # └cacheContFrame
  #  └cacheEntry[0,15]
  if 'guiCacheBtn' in data:
    data['guiCacheBtn'].config(state=tkinter.DISABLED)
    
  # create a separate window to view/edit the cache
  data['windowCache'] = windowCache = tkinter.Tk() # create the window
  windowCache.title("CSCI6461 Project Machine Cache") # name the window
  # if window is closed, destroy it
  windowCache.protocol("WM_DELETE_WINDOW", windowCache_onClose)
  # change disabled buttons to regular (black) text, label font to monospace
  style = ttk.Style(master=windowCache) # get style settings for windowMemory
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])
  style.configure("Courier.TLabel", font=('Courier', 12))

  # create a cache line number navigator, only top padding is needed
  cacheLineFrame = ttk.Frame(windowCache, padding=(0,10,0,0))
  cacheLineFrame.grid(column=0,row=0)
  data['cacheLineNum'] = cacheLineNum = labeledBitString(4) \
    .create(frame=cacheLineFrame, width=13, numLabels=False)
  # create display for next cache line to be replaced
  data['cacheNextNum'] = cacheNextNum = labeledBitString(4) \
    .create(frame=cacheLineFrame, text="Next Cache to Replace: ", x=6, padx=15, width=21, numLabels=False)
  
  # create a cache utility row, only bottom padding is needed
  cacheUtilFrame = ttk.Frame(windowCache)
  cacheUtilFrame.grid(column=0,row=1)
  # create a button to jump to the corresponding address in memory
  data['guiMemoryJumpBtn'] = guiMemoryJumpBtn = ttk.Button( \
    cacheUtilFrame, text="Show this block in memory")
  guiMemoryJumpBtn.grid(column=0,row=0)
  # create a check button for automatically show latest changed cache
  data['autoShowCacheBtn'] = autoShowCacheBtn = labeledBitString(1) \
    .create(frame=cacheUtilFrame, text="Show latest cache update: ", \
    x=2, padx=50, numLabels=False)
  
  # create a cache line properties display
  cachePropertyFrame = ttk.Frame(windowCache)
  cachePropertyFrame.grid(column=0,row=2)
  data['cacheInit'] = cacheInit = labeledBitString(1) \
    .create(frame=cachePropertyFrame, text="Initialized: ", x=0, numLabels=False)
  data['cacheDirty'] = cacheDirty = labeledBitString(1) \
    .create(frame=cachePropertyFrame, text="Dirty: ", x=2, padx=15, numLabels=False)
  data['cacheTag'] = cacheTag = labeledBitString(8) \
    .create(frame=cachePropertyFrame, text="Block Tag: ", x=4, padx=15)
    
  # create main body of cache editor, less top padding
  cacheContFrame = ttk.Frame(windowCache, padding=(10,5,10,10))
  cacheContFrame.grid(column=0,row=3)
  data['cacheEntry'] = cacheEntry = [0]*16
  for i in range(16):
    cacheEntry[i] = labeledBitString(16) \
      .create(frame=cacheContFrame, text=f"Word {i}: ", x=0, y=i+1)
  
  # add cache line navigator trigger and call once
  cacheLineNum.trigs["line_num_update"] = cacheLineUpdate
  cacheLineUpdate()
  # add cache replace display trigger and call once
  cacheNextNum.trigs["next_line_update"] = cache_next_update
  cache_next_update()

  # show the window, for use with PyCharm
  # see https://stackoverflow.com/questions/51253078/tkinter-isnt-working-with-pycharm/51261747
  # windowCache.mainloop()

def cleanCacheLine(cacheLine, update=True):
  # check if the give line in cache is clean
  # if not, clean it by saving its content to memory
  # since this is a write-back cache
  # this is the only place where memory gets written during simulation
  cache = data['cache']
  if cache[cacheLine][17] and cache[cacheLine][18]:
    # the line to use is both initialized and dirty
    blockAddr = cache[cacheLine][16] << 4
    for i in range(16): # save each word to memory
      data['memory'][blockAddr+i] = cache[cacheLine][i]
    memoryBlockUpdate()
  # line is now clean
  cache[cacheLine][18] = 0
  if update:
    cacheLineUpdate()
  
def checkHit(tag):
  # check if data we are accessing is already in cache (cache hit)
  # [tag] 8-bit integer for the block of memory (the first 8 bits of address)
  # returns the matching cache line [0,15] if hit, -1 if miss
  for i in range(16):
    if data['cache'][i][16] == tag and data['cache'][i][17] == 1:
      return i # tag match and the cache line is initialized
  return -1
  
def loadCache(tag, update=True):
  # loads tag into the cache, if it is not already loaded
  # returns the cache line containing the tag
  cache = data['cache']
  cacheLine = checkHit(tag)
  if cacheLine == -1: # cache miss
    # get pointer to next cache position to load
    cacheLine = cache[16]
    # clean cache line for overwriting, if it is not already clean
    cleanCacheLine(cacheLine, update=False) # update ater
    # write cache metadata (tag, init, dirty)
    cache[cacheLine][16] = tag
    cache[cacheLine][17] = 1
    # read memory and write data to cache
    blockAddr = tag << 4
    for i in range(16):
      cache[cacheLine][i] = data['memory'][blockAddr+i]
    if 'windowCache' in data and data['autoShowCacheBtn'].value():
      # want to change the cache page number
      # it automatically updates the gui
      data['cacheLineNum'].value_set(cacheLine, trigger=update)
    elif update: # update the cache gui
      cacheLineUpdate()
    # cache loaded, update pointer to the next cache position
    cache[16] = (cache[16] + 1) % 16
    # update the pointer display in cache window
    if 'windowCache' in data:
      data['cacheNextNum'].value_set(cache[16], trigger=False)
  return cacheLine

def cacheMemoryRead(address):
  # get the value from cache
  # if not in cache, access memory block and write its content to cache line
  # [address] 12-bit integer of the memory location
  wordNum = address & 0b1111
  tag = address >> 4
  cacheLine = loadCache(tag)
  # cache now hit at cache[cacheLine][wordNum]
  return data['cache'][cacheLine][wordNum]
  
def cacheMemoryWrite(address, value):
  # write the value to the cache
  # if not in cache, read the block
  cache = data['cache']
  wordNum = address & 0b1111
  tag = address >> 4
  # prepares the cache line to write to, update later
  cacheLine = loadCache(tag, update=False)
  # set value to the cache
  cache[cacheLine][wordNum] = value
  cache[cacheLine][18] = 1
  # update cache
  cacheLineUpdate()
  
def readFromMemory(address, indirect=False):
  # gets the value stored in memory, try to use cache first
  # updates MAR/MBR accordingly and returns the result
  # does not write to any main registers besides MAR and MBR
  # handles indirection, but not IX field (effective address should've been calculated already)
  # [address] integer, the location from memory to read from
  # [direct] boolean, specifies if it is a direct access
  # return -(fault ID)-1 if fault occurs
  # return [content] integer, the value stored in the memory location
  if address > 2047 or address < 0:
    fault(3) # Illegal Memory Address (memory installed)
    return -4
  data['MAR'].value_set(address)
  content = cacheMemoryRead(address)
  data['MBR'].value_set(content)
  if indirect: # indirection
    address = content
    if address > 2047 or address < 0:
      fault(3) # Illegal Memory Address (memory installed)
      return -4
    data['MAR'].value_set(address)
    content = cacheMemoryRead(address)
    data['MBR'].value_set(content)
  return content

def writeToMemory(address, value, indirect=False, checkReserve=True):
  # writes the value to address in memory, try to use cache first
  # updates MAR/MBR accordingly
  # does not write to any main registers besides MAR and MBR
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
    fault(3) # Illegal Memory Address (memory installed)
    return -4
  data['MAR'].value_set(address)
  if indirect: # indirection
    address = cacheMemoryRead(address)
    data['MBR'].value_set(address)
    if address > 2047 or address < 0:
      fault(3) # Illegal Memory Address (memory installed)
      return -4
    data['MAR'].value_set(address)
  # try to write the value to MBR and effective address in memory
  if checkReserve and address<6:
    fault(0) # Illegal Memory Address (reserved location)
    return -1
  data['MBR'].value_set(value)
  cacheMemoryWrite(address, value)
  memoryBlockUpdate()
  return 0