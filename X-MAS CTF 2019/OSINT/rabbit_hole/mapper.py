#!/usr/bin/python

newmap = {
# 2: "__PostFail__",
2: "",
4: "a",
5: "b",
6: "c",
7: "d",
8: "e",
9: "f",
10: "g",
11: "h",
12: "i",
13: "j",
14: "k",
15: "l",
16: "m",
17: "n",
18: "o",
19: "p",
20: "q",
21: "r",
22: "s",
23: "t",
24: "u",
25: "v",
26: "w",
27: "x",
28: "y",
29: "z",
30: "1",
31: "2",
32: "3",
33: "4",
34: "5",
35: "6",
36: "7",
37: "8",
38: "9",
39: "0",
40: "\n",
41: "__esc__",
42: "__del__",
43: "    ",
44: " ",
45: "-",
47: "[",
48: "]",
52: "'",
54: ",",
55: ".",
56: "/",
57: "^",
79: "__RightArrow__",
80: "__LeftArrow__"
}

final_string = ""

myKeys = open('scancodes.txt')
i = 1
for line in myKeys:
    bytesArray = bytearray.fromhex(line.strip())
    for byte in bytesArray:
        if byte != 0:
            keyVal = int(byte)

            if keyVal in newmap:
                final_string = final_string + newmap[keyVal]
            else:
                final_string = final_string + str(keyVal)
    i+=1

print (final_string)