from os import path
import re
import sys

if len(sys.argv) < 2:
    print("""Usage: python textbin.py IN_PATH [OUT_PATH]

Description:
Converts text files to binary format.

Arguments:
  IN_PATH      Path to the input file to be converted.
  [OUT_PATH]   Optional. Path to save the converted output file. If not provided, the converted file will be saved with the same name as the input file, suffixed with "_binary.txt" or "_text.txt" depending on the conversion direction.
""")
    input("Press enter to continue...")
    exit(0)
    
pain = sys.argv[1]

def split_list(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

with open(pain, 'r') as i:
    sl = i.readlines()

ext = 'bin'
s = ''
for i in sl:
    if i.startswith('#'):
        match (t:=i[1:].split())[0]:
            case 'ext':
                ext = t[1]
    else:
        s += i
paout = (path.join(path.split(pain)[0], path.basename(pain)+"."+ext)) if len(sys.argv) < 3 else sys.argv[2]
print(paout)

with open(paout, 'wb') as o:
    for i in split_list(s.replace(' ', '').replace('\n', ''), 2):
        o.write(bytes.fromhex(i))

input("Press enter to continue...")
