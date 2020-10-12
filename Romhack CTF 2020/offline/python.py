#!/usr/bin/python

import numpy as np
import scipy.misc as smp
import sqlite3 as lite
from PIL import Image
from bitstring import BitArray
import re

data = np.zeros( (64,128*7,3), dtype=np.uint8 )

f = open("data.bytes", "r")
lines = f.readlines()
img_index = 0
page_index = -1

for b_i, line in enumerate(lines):
    c = BitArray(hex=line)
    bits = re.findall('.',c.bin)
    col_index = b_i % 128
    if (col_index == 0):
        page_index = page_index + 1
    if (page_index == 8):
        page_index = 0
        col_index = 0
        img_index = img_index + 1
    for b_index, b in enumerate(bits):
        if int(b) == 1:
            data[63-((7-page_index)*8+b_index),img_index*128+(col_index)] = [0,0,0]
        else:
            data[63-((7-page_index)*8+b_index),img_index*128+(col_index)] = [255,255,255]
img = Image.fromarray(data, 'RGB')
img.save('flag.png')
