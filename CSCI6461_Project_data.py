# [data] dictionary of all data held by the program
#   including memory, registers, and gui elements
#   it is used by the console and many functions
# this file only serves to ensure [data] exists globally
if 'data' not in globals():
  data = {'memory': [0] * 2048}
