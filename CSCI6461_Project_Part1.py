import tkinter
from tkinter import ttk

class bit:
  # a class to define exactly one button to indicate/toggle the value of one binary bit
  def __init__(self, value=0):
    # constructor, prepares the button with fields (but not rendering it rightaway)
    # [value] integer, is the initial value to be filled in the binary bit
    # it will be either 0 or 1 (if non-zero)
    if value == 0:
      self.v = 0 # the value of the bit
    else:
      self.v = 1
    self.btn = None # where the actual tkinter button will bound to
    self.trigs = {} # triggers, a custom list of extra functions to call of button is clicked
    self.update() # immediately update once, might not be actually needed
  def update(self, trigger=True):
    # update the button's state
    # [trigger] boolean, determines if the list of custom triggers will be called
    if self.btn != None: # if physical button don't exist yet, don't do anything
      self.btn.config(text=str(self.v)) # update the text field of the button (to 0 or 1)
      if trigger:
        for t in self.trigs.keys():
          self.trigs[t]() # call each trigger function
    return self #(almost) always return self to allow daisy-chaining of method calls
  def flip(self):
    # flip the bit, self-explanatory
    if self.v == 0:
      self.v = 1
    else:
      self.v = 0
    return self.update() # update the button since value changed, it also returns self
  def destroy(self):
    # removes the button if it exists
    if self.btn != None:
      self.btn.destroy()
      self.btn = None
    return self #return self to allow daisy-chaining of method calls
  def create(self,frame,x,y,**kwargs):
    # actually render the button on the GUI
    # arguments:
    # [frame] tkinter's frame, determines the frame where the button will be placed
    # [x,y] integer >= 0, determines position of button from the top left of frame
    # [**kwargs] any additional custom arguments for the tkinter button
    self.destroy() # only one button per instance allowed, so destroy previous one
    self.btn = ttk.Button(frame, style="TButton",**kwargs) # call ttk to create button
    self.btn.grid(column=x,row=y) # actually place the button in the GUI
    # set the display text to be the value of the button
    # set up trigger: calls flip(self) when it is clicked
    self.btn.config(text=str(self.v), command=lambda: self.flip())
    return self #return self to allow daisy-chaining of method calls

class bitString:
  # a "string" of many bit class instances, with some helper functions
  def __init__(self, count=1):
    # constructor, prepares the list of bits
    # [count] integer, the number of bit instances
    self.count = count
    self.bits = [] # actual list of bit instances
    self.trigs = {} # triggers, custom list of functions to call when things update
    for i in range(count):
      self.bits.append(bit()) # create all the bit instances
  def update(self,trigger=True):
    # make updates when value changes
    # [trigger] boolean, if custom triggers will be called
    if trigger:
      for t in self.trigs.keys():
        self.trigs[t]()
    return self # return self for chaining
  def value(self):
    # just a shorthand version of value_get(self)
    return bitString.value_get()
  def value_get(self):
    # get the number this string of bit represents
    # lower index bit is more significant (big-endian)
    sum = 0
    for i in range(self.count):
      # add 2^(position of the bit) if it is 1
      sum += self.bits[i].v * (2 ** (self.count - i - 1))
    return sum # rare case when a number (instead of self) is returned
  def value_set(self, value):
    # tries to set the string to the provided value
    # [value] integer, to be set
    remainder = value
    for i in range(self.count):
      if remainder <= 0:
        break # we are done
      if remainder >= (2 ** (self.count - i - 1)):
        # change a bit to 1 to accomodate some of the remainder value
        self.bits[i].v = 1
        remainder -= (2 ** (self.count - i - 1))
      else:
        # this bit represents a value larger than current remainder
        self.bits[i].v = 0
      # update each bit button, but don't call their custom triggers
      # (custom triggers for this case should be set for this bitString class instead)
      self.bits[i].update(trigger=False)
    # call the custom triggers
    self.update()
    # returns the remainder of number that couldn't be placed in the string
    # possible reason 1: the provided [value] is negative
    #   then [value] is returned because this can't store negative values
    # possible reason 2: the provided [value] is too large to fit
    #   then whatever remaining portion is returned
    # if it returns 0, then the value is correctly set
    return remainder # rare case when a number (instead of self) is returned
  def bitStyle(self, **kwargs):
    # set all the bits in the bitString with style [**kwargs]
    for bit in bits:
      if bit.btn != None:
        bit.btn.config(**kwargs)
    return self
  def destroy(self):
    # destroy all the bit instances
    for i in range(self.count):
      self.bits[i].destroy()
    return self # return self for chaining
  def create(self, frame, x=0, y=0, **kwargs):
    # render the entire string of bit on GUI
    # [frame] tkinter frame, where to place the bits
    # [x,y] integer, position of the string
    #   (the string will always be rendered horizontally from there)
    # [**kwargs] additional custom arguments for the tkinter button
    self.destroy() # only one string per instance, so destroy previous one
    for i in range(self.count):
      self.bits[i].create(frame, x+i, y, **kwargs) # call bit class' create method
      # add update(self) to the trigger list of every bit instance
      # so it gets called when the bit updates
      self.bits[i].trigs["bitString_update"] = lambda: self.update()
    return self # return self for chaining
    
class labeledBitString:
  # a bitString with some common tkinter labels (text fields)
  def __init__(self, count=1):
    # constructor, prepares the bitString and the labels
    self.bitStr = bitString(count=count)
    self.labelTxt = None # label for the name of the bitString
    self.labelHex = None # label for the value of bitString in hex
    self.labelTen = None # label for the value of bitString in base-Ten
  def value(self):
    # just a shorthand version of value_get(self)
    return self.value_get()
  def value_get(self):
    # just call the bitStr value_get()
    return self.bitStr.value_get()
  def value_set(self, value):
    # just call the bitStr value_set()
    self.bitStr.value_set(value)
    return self # return self for chaining
  def trigs(self):
    # just return bitStr's list of custom triggers
    return self.bitStr.trigs
  def update(self, trigger=True):
    # make updates to labels when value changes
    # [trigger] Boolean, doesn't do anything
    #   is just here to keep same format as other update() methods
    if self.labelHex != None: # update labelHex to new hex value
      self.labelHex.config(text=hex(self.value_get()))
    if self.labelTen != None: # update labelTen to new base-ten value
      self.labelTen.config(text=str(self.value_get()))
    return self
  def bitStyle(self, **kwargs):
    # set the style of individual bit instances within bitStr
    # [**kwargs] parameter to set the bit instances
    self.bitStr.bitStyle(**kwargs)
    return self # return self for chaining
  def destroyLabel(self, label):
    # helper method to destroy particular label
    try: # trying in case label is already distroyed
      label.destroy()
    except:
      # if already destroyed, label.destroy() gives exception (error)
      # we can safely ignore it
      pass
    finally:
      label = None # reset the field value
    return self # return self for chaining
  def destroy(self):
    # just call destroy for every part
    self.bitStr.destroy()
    self.destroyLabel(self.labelTxt)
    self.destroyLabel(self.labelHex)
    self.destroyLabel(self.labelTen)
    return self # return self for chaining
  def create(self, frame, text, x=0, y=0, gap=0, toggleAble=True, **kwargs):
    # create the entire row of labeled bitString
    # [frame] tkinter frame, where to place everything
    # [text] string, the name of the row, will be placed in self.labelTxt
    # [x,y] integer, position of the row
    #   (the row will always be rendered horizontally from there)
    # [gap] integer, shifts the bit buttons to the right
    #   to help align them with other rows
    # [toggleAble] boolean, if false, the buttons can't be clicked
    # [**kwargs] additional custom arguments for the self.labelTxt label
    #   (for the style of the bottons, use self.bitStyle(**kwargs))
    #   (for other non-style properties of the buttons,
    #     you'd have to modify self.bitStr.bits individually)
    self.destroyLabel(self.labelTxt) # remake the labels
    self.labelTxt = ttk.Label(frame, text=text, **kwargs)
    self.labelTxt.grid(column=x, row=y) # place the name label first
    value = self.bitStr.value_get() # get the bitStr value for the next 2 labels
    self.destroyLabel(self.labelHex) # remake the labels
    self.labelHex = ttk.Label(frame, text=hex(value), width=6)
    self.labelHex.grid(column=x+1, row=y) # place the label 1 to the right
    self.destroyLabel(self.labelTen) # remake the labels
    self.labelTen = ttk.Label(frame, text=str(value), width=6)
    self.labelTen.grid(column=x+2, row=y) # place the label 2 to the right
    # create the bitString
    # [x] is shifted to the right by 3 to fit the 3 labels
    #   then by [gap] as specified by the method caller for alignment
    # [width=2] is a custom **kwargs argument that sets the width of the buttons
    # [state] is tkinter.NORMAL if it can be toggled
    #   tkinter.DISABLED if it can't
    self.bitStr.create(frame, x=x+3+gap, y=y, width=2, state=(tkinter.NORMAL if toggleAble else tkinter.DISABLED))
    # add the update trigger function to self.bitStr
    self.bitStr.trigs["label_update"] = lambda: self.update()
    return self # return self for chaining

# Start making all the interface related stuffs
# we have widgets placed in a frame, and frames places in a window
# position is defined in x(column) and y(row)
# x=0,y=0 is the top left, going right/down is the positive x/y direction
windowInterface = tkinter.Tk() # create the GUI window
windowInterface.winfo_toplevel().title("CSCI6461 Project Machine Interface") # name the window
style = ttk.Style(master=windowInterface) # get style settings for windowInterface
# the original ttk style for disabled buttons have gray text, which is hard to read
#   so change it to regular (black) text
style.map("TButton", foreground=[("disabled", "SystemWindowText")])

# create a frame in the window to fit first batch of registers
registersMain = ttk.Frame(windowInterface, padding=10)
registersMain.grid(column=0,row=0) # place the frame
# create each row of the registers by calling class methods above
#   for what each of these parameters do, read the class method definition above
PC = labeledBitString(12).create(frame=registersMain, text="PC:", x=0, y=0, gap=4, width=4)
MAR = labeledBitString(12).create(frame=registersMain, text="MAR:", x=0, y=1, gap=4, width=5)
MBR = labeledBitString(16).create(frame=registersMain, text="MBR:", x=0, y=2, gap=0, width=5)
IR = labeledBitString(16).create(frame=registersMain, text="IR:", x=0, y=3, gap=0, width=4)
MFR = labeledBitString(4).create(frame=registersMain, text="MFR:", x=0, y=4, gap=12, width=5, toggleAble=False)
Priviledged = labeledBitString(1).create(frame=registersMain, text="Priviledged: ", x=0, y=5, gap=15, width=12, toggleAble=False)

# create a frame to fit GPR and IXR
registersGPR = ttk.Frame(windowInterface, padding=10)
registersGPR.grid(column=1,row=0) # place the frame, note that this is on the left of registersMain
GPR,IXR = [None]*4,[None]*4 # initialize list for the registers
for i in range(4): # create all 4 GPR registers
  GPR[i] = labeledBitString(16).create(frame=registersGPR, text="GPR "+str(i)+":", x=0, y=i, gap=0, width=6)
for i in range(1,4): # create all 3 IXR registers
  IXR[i] = labeledBitString(16).create(frame=registersGPR, text="IXR "+str(i)+":", x=0, y=i+4, gap=0, width=6)
# create a small spacer between GPR and IXR, just to make things look better
spacerGPR = ttk.Label(registersGPR, text="")
spacerGPR.grid(column=0,row=4)

# create a separate window to view/edit the memory
windowMemory = tkinter.Tk() # create the window
windowMemory.winfo_toplevel().title("CSCI6461 Project Machine Memory") # name the window
style = ttk.Style(master=windowMemory) # get style settings for windowMemory
# change disabled buttons to regular (black) text
style.map("TButton", foreground=[("disabled", "SystemWindowText")])

memoryPageFrame = ttk.Frame(windowMemory, padding=10)
memoryPageFrame.grid(column=0,row=0)
memoryPageNum = labeledBitString(12).create(frame=memoryPageFrame, text="Memory Page Number:", x=0, y=0, gap=4, width=24)
memoryPageNum.bitStr.bits[0].btn.config(state=tkinter.DISABLED)
memoryContFrame = ttk.Frame(windowMemory, padding=10)
memoryContFrame.grid(column=0,row=1)

memory = [0]*2048 #

# a temporary (very janky) field console to run custom commands
# this is not safe--there's very little preventing you from going "rm -rf" here
# so know what you are doing and don't do dangerous stuff
while True:
  # globals() are the function definitons and variables above
  #   so you can use/modify them as you wish
  exec(input(">>> "),globals())