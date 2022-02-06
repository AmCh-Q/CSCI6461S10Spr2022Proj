import tkinter
from tkinter import ttk

class bit:
  # a class to define exactly one button to indicate/toggle the value of one binary bit
  def __init__(self, value=0):
    # constructor, prepares the button with properties (but not rendering it rightaway)
    # [value] integer, is the initial value to be filled in the binary bit
    # it will be either 0 or 1 (if non-zero)
    # [self.v] 0 or 1, the value of the bit held
    # [self.btn] ttk.Button, where the actual tkinter button will bound to
    # [self.trigs] list, a custom list of functions to call when button is clicked
    self.btn = None
    self.trigs = {}
    self.value_set(value)
  def update(self, trigger=True):
    # update the button's state
    # [trigger] boolean, determines if the list of custom triggers will be called
    if self.btn != None: # if physical button don't exist yet, don't do anything
      self.btn.config(text=str(self.v)) # update the text field of the button (to 0 or 1)
      if trigger:
        for t in self.trigs.keys():
          self.trigs[t]() # call each trigger function
    return self #(almost) always return self to allow chaining of method calls
  def value(self):
    return self.v
  def value_get(self):
    return self.v
  def value_set(self, value=0, trigger=True):
    # set v to 0 or 1
    # [value] integer
    # [trigger] boolean, whether custom triggers will be called
    if value == 0:
      self.v = 0
    else:
      self.v = 1
    self.update(trigger=trigger)
    return 0
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
    return self #return self to allow chaining of method calls
  def create(self, frame, x=0, y=0, **kwargs):
    # actually render the button on the GUI
    # arguments:
    # [frame] tkinter's frame, determines the frame where the button will be placed
    # [x,y] integer >= 0, determines position of button from the top left of frame
    # [**kwargs] any additional custom arguments for the tkinter button
    self.destroy() # only one button per instance allowed, so destroy previous one
    # call ttk to create button
    # [text] value (0 or 1) of the button
    # [command] calls flip(self) when it is clicked
    self.btn = ttk.Button( \
      frame, text=str(self.v), command=lambda: self.flip(), style="TButton",**kwargs)
    self.btn.grid(column=x, row=y) # place the button in the GUI
    return self #return self to allow chaining of method calls

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
    return self.value_get()
  def value_get(self):
    # get the number this string of bit represents
    # lower index bit is more significant (big-endian)
    sum = 0
    for i in range(self.count):
      # add 2^(position of the bit) if it is 1
      sum += self.bits[i].v * (2 ** (self.count - i - 1))
    return sum # rare case when a number (instead of self) is returned
  def value_set(self, value, trigger=True):
    # tries to set the string to the provided value
    # [value] integer, to be set
    # [trigger] boolean, whether custom triggers will be called
    remainder = value
    for i in range(self.count):
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
    self.update(trigger=trigger)
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
  def create(self, frame, x=0, y=0, toggleAble=True, **kwargs):
    # render the entire string of bit on GUI
    # [frame] tkinter frame, where to place the bits
    # [x,y] integer, position of the string
    #   (the string will always be rendered horizontally from there)
    # [toggleAble] boolean, if false, the buttons can't be clicked
    # [**kwargs] additional custom arguments for the tkinter button
    self.destroy() # only one string per instance, so destroy previous one
    buttonState = tkinter.NORMAL if toggleAble else tkinter.DISABLED
    for i in range(self.count):
      # call bit class' create method
      self.bits[i].create(frame=frame, x=x+i, y=y, state=buttonState, **kwargs)
      # add update(self) to the trigger list of every bit instance
      # so it gets called when the bit updates
      self.bits[i].trigs["bitString_update"] = lambda: self.update()
    return self # return self for chaining
    
class labeledBitString(bitString):
  def __init__(self, count=1):
    # constructor, prepares the bitString and value labels
    # [count] integer, simply passed for bitString.__init__()
    super().__init__(count=count) # call bitString.__init__ to initialize
    self.labelTxt = None # label for the name of the bitString
    self.labelHex = None # label for the value of bitString in hex
    self.labelTen = None # label for the value of bitString in base-Ten
  def update(self, trigger=True):
    # make updates to labels when value changes
    # [trigger] Boolean, simply passed for bitString.update()
    super().update(trigger=trigger)
    if self.labelHex != None: # update labelHex to new hex value
      self.labelHex.config(text=f"{self.value():#0{6}X}".replace("X","x"))
    if self.labelTen != None: # update labelTen to new base-ten value
      self.labelTen.config(text=str(self.value()))
    return self
  def text_set(self, text=""):
    if self.labelTxt != None:
      self.labelTxt.config(text=text)
    return self
  def destroyLabel(self, label):
    # helper method to destroy particular label
    if label != None:
      # label.winfo_exists() returns 0 if already destroyed
      if label.winfo_exists() > 0: # need to destory first
        label.destroy()
      label = None # reset
    return self # return self for chaining
  def destroy(self):
    # calls destroy for every part
    super().destroy()
    self.destroyLabel(self.labelTxt)
    self.destroyLabel(self.labelHex)
    self.destroyLabel(self.labelTen)
    return self # return self for chaining
  def create(self, frame, text="", x=0, y=0, gap=0, toggleAble=True, numLabels=True, **kwargs):
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
    # destroy labels first to remake the labels
    self.destroyLabel(self.labelTxt)
    self.destroyLabel(self.labelHex)
    self.destroyLabel(self.labelTen)
    # make the labels to display the number in the register (base ten and hex)
    # [width] is for the maximum width the string can be, just enough to fit
    # [column] is shifted by x(configed value)
    #   and possibly gap+self.count(to fit the buttons)
    #   and 0-2 (to fit the previous labels)
    # [row] is shifted by y(configured value)
    # [sticky] is tkinter.W to mean left alignment for text
    # [padx] is for a bit extra padding, just to look better
    value = self.value() # get the bitStr value for the labels
    self.labelTxt = ttk.Label(frame, text=text, **kwargs)
    self.labelTxt.grid(column=x, row=y, sticky = tkinter.W)
    if numLabels:
      self.labelHex = ttk.Label(frame, \
        text=f"{value:#0{6}X}".replace("X","x"), width=6, style="Courier.TLabel")
      self.labelHex.grid(column=x+gap+self.count+1, row=y, sticky = tkinter.W, padx=(5,0))
      self.labelTen = ttk.Label(frame, text=str(value), width=5, style="Courier.TLabel")
      self.labelTen.grid(column=x+gap+self.count+2, sticky = tkinter.W, row=y)
    # create the bitString
    # [x] is shifted to the right by 3 to fit the 3 labels
    #   then by [gap] as specified by the method caller for alignment
    # [width=2] is a custom **kwargs argument that sets the width of the buttons
    # [state] is tkinter.NORMAL if it can be toggled
    #   tkinter.DISABLED if it can't
    buttonState = tkinter.NORMAL if toggleAble else tkinter.DISABLED
    for i in range(self.count):
      # call bit class' create method
      self.bits[i].create(frame=frame, x=x+i+1+gap, y=y, width=2, state=buttonState)
      # add update(self) to the trigger list of every bit instance
      # so it gets called when the bit updates
      self.bits[i].trigs["labeledBitString_update"] = lambda: self.update()
    return self # return self for chaining
