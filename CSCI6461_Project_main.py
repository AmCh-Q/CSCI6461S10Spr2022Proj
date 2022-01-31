import tkinter
from tkinter import ttk
from CSCI6461_Project_gui_interface import *
from CSCI6461_Project_data import *

def main():  
  # initializes memory
  data['memory'] = [0]*2048
  
  # create the gui window, writes to data
  guiInterface()

  # a temporary (very janky) field console to run custom commands
  # this is not safe--there's very little preventing you from going "rm -rf" here
  # so know what you are doing and don't do dangerous stuff
  while True:
    # globals() are the function definitons and variables above
    #   so you can use/modify them as you wish
    try:
      exec(input(">>> "), globals(), data)
    except Exception as e:
      print(e)

if __name__ == '__main__':
  main()
  