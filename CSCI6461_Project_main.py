import tkinter
from tkinter import ttk
from CSCI6461_Project_gui_interface import *

def main():
  # [localVar] list of local variables that will be written by other functions
  #   it is used by the console
  localVar = {}
  
  # initializes memory
  localVar['memory'] = [0]*2048
  
  # create the gui window, writes to localVar
  guiInterface(localVar)

  # a temporary (very janky) field console to run custom commands
  # this is not safe--there's very little preventing you from going "rm -rf" here
  # so know what you are doing and don't do dangerous stuff
  while True:
    # globals() are the function definitons and variables above
    #   so you can use/modify them as you wish
    try:
      exec(input(">>> "), globals(), localVar)
    except Exception as e:
      print(e)

if __name__ == '__main__':
  main()
  