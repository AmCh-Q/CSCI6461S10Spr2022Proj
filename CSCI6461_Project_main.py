from CSCI6461_Project_gui_interface import *
from CSCI6461_Project_data import *

def main():  
  # initializes memory and cache
  data['memory'] = [0]*2048
  data['cache'] = [[0]*19 for i in range(16)]+[0]
  
  # create the gui window, writes to data
  guiInterface()

  # a temporary (very janky) field console to run custom commands
  # this is not safe--there's very little preventing you from going "rm -rf" here
  # so know what you are doing and don't do dangerous stuff
  # also does not work with tk.mainloop(), so no way to run this in PyCharm
  while True:
    # globals() are the function definitions and variables above,
    #   so you can use/modify them as you wish
    try:
      exec(input(">>> "), globals(), data)
    except Exception as e:
      print(e)

if __name__ == '__main__':
  main()
