opDict = {
  'HLT':0,
  'TRAP':24,
  'LDR':1,
  'STR':2,
  'LDA':3,
  'LDX':33,
  'STX':34,
  'JZ':8,
  'JNE':9,
  'JCC':10,
  'JMA':11,
  'JSR':12,
  'RFS':13,
  'SOB':14,
  'JGE':15,
  'AMR':4,
  'SMR':5,
  'AIR':6,
  'SIR':7,
  'MLT':16,
  'DVD':17,
  'TRR':18,
  'AND':19,
  'ORR':20,
  'NOT':21,
  'SRC':25,
  'RRC':26,
  'IN':49,
  'OUT':50,
  'CHK':51,
  'FADD':27,
  'FSUB':28,
  'VADD':29,
  'VSUB':30,
  'CNVRT':31,
  'LDFR':40,
  'STFR':41
}

while True:
  string=input("Enter Instruction: ")
  tokens=string.replace(',',' ').split()
  instruction=0
  opcode = 0
  if tokens[0] in opDict:
    opcode = opDict[tokens[0]]
    instruction += (opcode<<10)
  r = 0
  if opcode in [1,2,3,8,9,10,14,15,4,5,6,7,16,17,18,19,20,21,25,26,49,50,51,27,28,29,30,31,40,41]:
    r = int(tokens[1])
    instruction += (r<<8)
  ix = 0
  if opcode in [1,2,3,33,34,8,9,10,11,14,15,4,5,16,17,18,19,20]:
    if opcode in [33,34,11,12]:
      ix = int(tokens[1])
    if opcode in [1,2,3,8,9,10,14,15,4,5,16,17,18,19,20]:
      ix = int(tokens[2])
    instruction += (ix<<6)
  al,lr,count=0,0,0
  if opcode in [25,26]:
    al,lr,count=int(tokens[4]),int(tokens[3]),int(tokens[2])
    instruction += (al<<7)
    instruction += (lr<<6)
    instruction += count
  devid = 0
  if opcode in [49,50,51]:
    devid = int(tokens[2])
    instruction += devid
  vi,vx = 0,0
  if opcode in [27,28,29,30,31,40,41]:
    vi=int(tokens[4])
    vx=int(tokens[2])
    instruction += (vi<<7)
    instruction += (vx<<5)
  i = 0
  address = 0
  if opcode in [1,2,3,33,34,8,9,10,11,12,13,14,15,4,5,6,7,27,28,29,30,31,40,41]:
    if opcode in [13]:
      address = tokens[1]
    if opcode in [33,34,6,7]:
      address = tokens[2]
    if opcode in [11,12]:
      address = tokens[2]
    if opcode in [4,5,27,28,29,30,31,40,41]:
      address = tokens[3]
    if opcode in [1,2,3,8,9,10,14,15,4,5,27,28,29,30,31,40,41]:
      address = tokens[3]
    instruction += int(address)
  if opcode in [1,2,3,33,34,8,9,10,11,14,15,4,5]:
    if opcode in [33,34,11,12]:
      i = tokens[3]
    if opcode in [1,2,3,8,9,10,14,15,4,5]:
      i = tokens[4]
    instruction += (int(i)<<5)
  print(f"{instruction:016b}")
  print(f"0x{instruction:04x}")
  print(f"{instruction}")