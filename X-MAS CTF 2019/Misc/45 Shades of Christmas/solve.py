
#!/usr/bin/env python3
#(metantz)


from PIL import Image
import numpy
import base64


image = Image.open("grey.bmp")
matrix = numpy.array(image)
res = ""

#extract grey value by columns
for i in range(len(matrix)):
        for j in range(len(matrix)):
                g = matrix[j][i][1]
                res += hex(g)[-2:]

print(base64.b64decode(bytearray.fromhex(res).decode()))
