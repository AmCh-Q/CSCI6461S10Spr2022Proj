import tkinter
from tkinter import ttk
from CSCI6461_Project_data import *

def windowIo_onClose():
  # trigger function when i/o interface is closed
  if 'windowIo' in data:
    data['inputText'] = data['ioKeyboardText'].get('1.0','end-1c')
    # destroy and remove record of the window
    data['windowIo'].destroy()
    del data['windowIo']
  if 'guiIoBtn' in data:
    # re-enable the button in optionsFrame for reopening i/o
    data['guiIoBtn'].config(state=tkinter.NORMAL)
    
def ioUpdate():
  # trigger function when saved text changes, need to update the widgets
  # do nothing if io window isn't open
  if 'windowIo' not in data:
    return
  ioPrinterText = data['ioPrinterText'] # get the printer widget
  if ioPrinterText.get('1.0','end-1c') != data['printText']:
    ioPrinterText.config(state=tkinter.NORMAL) # Enable editing
    ioPrinterText.delete('1.0', tkinter.END)
    ioPrinterText.insert('1.0', data['printText'])
    ioPrinterText.config(state=tkinter.DISABLED) # Disable editing
    ioPrinterText.yview(tkinter.END) # scroll to the very end to show the text
  
  ioKeyboardText = data['ioKeyboardText'] # get the keyboard widget
  if ioKeyboardText.get('1.0','end-1c') != data['inputText']:
    ioKeyboardText.delete('1.0', tkinter.END)
    ioKeyboardText.insert('1.0', data['inputText'])
    ioKeyboardText.yview(tkinter.END) # scroll to the very end to show the text

def guiIo():
  # start making interface for input/output
  # GUI Structure:
  # windowIo
  # └ioFrame
  #  ├ioPrinterLabel
  #  ├ioPrinterText
  #  ├ioKeyboardLabel
  #  ├ioKeyboardText
  #  └ioKeyboardBtn
  
  # disable the "open i/o interface" button to prevent opening it again
  if 'guiIoBtn' in data:
    data['guiIoBtn'].config(state=tkinter.DISABLED)
  if 'windowIo' in data: # somehow io window is already open
    return
  # create a separate window for the I/O
  data['windowIo'] = windowIo = tkinter.Tk() # create the window
  windowIo.title("CSCI6461 Project Input/Output") # name the window
  # if window is closed, destroy it
  windowIo.protocol("WM_DELETE_WINDOW", windowIo_onClose)
  # change disabled buttons to regular (black) text, label font to monospace
  style = ttk.Style(master=windowIo) # get style settings for windowIo
  style.map("TButton", foreground=[("disabled", "SystemWindowText")])
  style.configure("Courier.TLabel", font=('Courier', 12))
  
  # create a frame to hold all i/o widgets
  ioFrame = ttk.Frame(windowIo, padding=10)
  ioFrame.grid(column=0,row=0)
  
  # create the tkinter label and textbox for the console printer
  data['ioPrinterLabel'] = ioPrinterLabel = ttk.Label(ioFrame, text="Console Printer")
  ioPrinterLabel.grid(column=0,row=0)
  data['ioPrinterText'] = ioPrinterText = tkinter.Text(ioFrame, width=50, height=10)
  ioPrinterText.grid(column=0,row=1)
  ioPrinterText.insert('1.0', data['printText'])
  ioPrinterText.config(state=tkinter.DISABLED) # Disable editing
  ioPrinterText.yview(tkinter.END) # scroll to the very end to show the text
  
  # create the tkinter label and textbox for the console keyboard
  data['ioKeyboardLabel'] = ioKeyboardLabel = ttk.Label(ioFrame, text="Console Keyboard")
  ioKeyboardLabel.grid(column=0,row=2)
  data['ioKeyboardText'] = ioKeyboardText = tkinter.Text(ioFrame, width=50, height=10)
  ioKeyboardText.grid(column=0,row=3)
  ioKeyboardText.insert('1.0', data['inputText'])
  ioKeyboardText.yview(tkinter.END) # scroll to the very end to show the text

  # show the window, for use with PyCharm
  # see https://stackoverflow.com/questions/51253078/tkinter-isnt-working-with-pycharm/51261747
  # windowIo.mainloop()

def splitInstuctionIo(instruction):
  # [instruction] 16-bit integer (0-65535)
  # splits into opcode(6), r(2), unused(3), devid(5) in that order
  # for i/0 instructions
  # the unused(3) bits of the instruction are ignored
  opcode = instruction >> 10
  r = (instruction >> 8) & 0b11
  devid = instruction & 0b11111
  return opcode,r,devid

def ioPrint(string, newLine=False):
  # Print text to the user in the console printer
  # [string] string, the text to print
  # [newLine] boolean, whether the print should be in its own line
  if 'windowIo' not in data:
    guiIo()
    data['windowIo'].after(1, lambda: data['windowIo'].focus_force()) # force focus window
  ioPrinterText = data['ioPrinterText'] # get the printer widget
  # enable editing to write changes
  ioPrinterText.config(state=tkinter.NORMAL)
  if newLine:
    # get the last character of the text
    lastChar = ioPrinterText.get('end-2c','end-1c')
    if lastChar != '' and lastChar != '\n':
      # start a new line if the last string didn't end with one
      ioPrinterText.insert(tkinter.END, '\n')
  ioPrinterText.insert(tkinter.END, string) # print the text
  ioPrinterText.config(state=tkinter.DISABLED) # disable editing
  ioPrinterText.yview(tkinter.END) # scroll to the very end to show the text
  data['printText'] = ioPrinterText.get('1.0','end-1c') # update text
  
def ioKey():
  # Get a character from the console keyboard
  # returns the string
  if 'ioKeyboardText' in data:
    # get the full string of the keyboard widget
    # the last character is always '\n' even when widget is empty so we ignore that character
    # see https://tkdocs.com/tutorial/text.html
    data['inputText'] = data['ioKeyboardText'].get('1.0','end-1c')
  if len(data['inputText']) > 0:
    character = data['inputText'][0]
    data['inputText'] = data['inputText'][1:]
    if 'ioKeyboardText' in data:
      data['ioKeyboardText'].delete('1.0') # remove the first character from Keyboard
    return ord(character)
  if 'windowIo' not in data:
    guiIo()
    data['windowIo'].after(1, lambda: data['windowIo'].focus_force()) # force focus window
  return 0

def ioInstExec(instruction):
  opcode,r,devid = splitInstuctionIo(instruction)
  if opcode == 49: # IN instruction
    if devid == 0: # console keyboard
      value = ioKey() # get the value of the first character from Keyboard
      data["GPR"][r].value_set(value % (1<<16)) # incase of overflow, truncate the bits
  elif opcode == 50: # OUT instruction
    value = data["GPR"][r].value() # get the value from the register
    character = chr(value) # convert the value to a character
    if devid == 1: # console printer
      ioPrint(character) # send the text to the printer
  elif opcode == 51: # CHK instruction
    value = 0
    if devid == 0: # console keyboard
      if 'ioKeyboardText' in data:
        data['inputText'] = data['ioKeyboardText'].get('1.0','end-1c')
      value = len(data['inputText']) # get length
      if value == 0: # force focus window to ask for input
        if 'windowIo' not in data:
          guiIo()
          data['windowIo'].after(1, lambda: data['windowIo'].focus_force()) # force focus window
    elif devid == 1: # console printer
      if 'ioPrinterText' in data:
        data['printText'] = data['ioPrinterText'].get('1.0','end-1c')
      value = len(data['printText']) # get length
    data["GPR"][r].value_set(value % (1<<16)) # incase of overflow, truncate the bits
  return 0
      