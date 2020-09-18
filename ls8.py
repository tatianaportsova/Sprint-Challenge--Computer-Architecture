# python3 ls8.py sctest.ls8

import sys
from cpu import *

cpu = CPU()
cpu.load(sys.argv[1])
cpu.run()