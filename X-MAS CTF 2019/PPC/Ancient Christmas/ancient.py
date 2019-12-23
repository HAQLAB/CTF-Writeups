#!/usr/bin/python3
#(coire1)

# import string
# import os
import subprocess
import re
import cv2
from PIL import Image
import numpy as np
import copy
import base64
from joblib import Parallel, delayed
import glob
import binascii
import io
import time
import socket

HOST = 'challs.xmas.htsp.ro'  # The server's hostname or IP address
PORT = 14001        # The port used by the server
DICT = b'/media/hdd1/Downloads/5chars.txt.sha256'
CPU_COUNT = 8

S_COUNT = {
    0: {
        'matches': [],
        'count': 0
    },
    1: {
        'matches': [],
        'count': 0
    },
    2: {
        'matches': [],
        'count': 0
    },
    3: {
        'matches': [],
        'count': 0
    },
    4: {
        'matches': [],
        'count': 0
    },
    5: {
        'matches': [],
        'count': 0
    },
}

class Solver():
    def __init__(self):
        print("Starting...")
        self.symbols = []
        self.colors = []

        # Each level
        self.symbols_count = {}
        self.cache_count = {}
        self.cache_image = False

        # Socket
        self.mainSocket = False

        # Timings
        self.globalStart = time.time()
        self.globalEnd = 0
        self.tempStart = 0
        self.tempEnd = 0

        # Start after initialization
        self.start()



    def init_recognition(self):
        for i in range(0, 6):
            for file in glob.glob("templates/{}/*.png".format(i)):
                im = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
                self.symbols.append({
                    'image': im,
                    'name': i
                })
        self.colors.append((0, 0, 255))
        self.colors.append((255, 0, 255))
        self.colors.append((0, 255, 0))
        self.colors.append((255, 0, 0))
        self.colors.append((0, 255, 255))
        self.colors.append((255, 255, 0))

    def parse_errors(self, data):
        if b'time!' in data:
            self.log('Wrong answer!')
            self.save_error()
            return self.end()
        elif b'criterion' in data:
            print('Wrong criterion')
            return self.end()
        elif b'faster!' in data:
            self.log('Too slow!')
            self.save_error()
            return self.end()
        elif b'}' in data:
            self.log('Fuck you!')
            self.save_error()
            return self.end()
        return True


    def recvuntil(self):
        data = self.mainSocket.recv(65536)
        errors = self.parse_errors(data)
        if errors:
            while b',5)' not in data:
                data = data + self.mainSocket.recv(65536)
        return data.strip()

    def recvbanner(self, level):
        if (level == 1):
            data = self.mainSocket.recv(63)
        elif (level == 10):
            data = self.mainSocket.recv(61)
        elif (level == 11):
            data = self.mainSocket.recv(4096)
        else:
            data = self.mainSocket.recv(60)
        self.log(data)
        return self.parse_errors(data)



    def send(self, msg):
        self.log(msg)
        self.mainSocket.send(msg + b'\n')
        return True

    def check_already_counted(self, i, pt):
        matches = self.symbols_count[i]['matches']
        for m in matches:
            min_x = m[0] - 20
            max_x = m[0] + 20
            min_y = m[1] - 20
            max_y = m[1] + 20
            in_x = (pt[0] > min_x and pt[0] < max_x)
            in_y = (pt[1] > min_y and pt[1] < max_y)
            if (in_x and in_y):
                return False
        return True

    def match_template(self, symbol, large_image):
        result = cv2.matchTemplate(large_image, symbol['image'], cv2.TM_CCOEFF_NORMED)
        threshold = .6
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):
            if self.check_already_counted(symbol['name'], pt):
                self.symbols_count[symbol['name']]['matches'].append(pt)
                self.symbols_count[symbol['name']]['count'] = self.symbols_count[symbol['name']]['count'] + 1

    def count_symbols(self, level, large_image):
        self.symbols_count = copy.deepcopy(S_COUNT)
        stats = Parallel(
            n_jobs=CPU_COUNT,
            require='sharedmem'
        )(delayed(self.match_template)(symbol, large_image) for symbol in self.symbols)
        self.cache_count = self.symbols_count
        return "{},{},{},{},{},{}".format(
            self.symbols_count[0]['count'],
            self.symbols_count[1]['count'],
            self.symbols_count[2]['count'],
            self.symbols_count[3]['count'],
            self.symbols_count[4]['count'],
            self.symbols_count[5]['count']
        ).encode()

    def read_image(self, data, level):
        d = data[2:][:-1]
        decoded = base64.b64decode(d)
        image = io.BytesIO(decoded)
        img = Image.open(image)
        self.cache_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        return self.cache_image

    def save_error(self):
        print("Saving images...")
        self.globalEnd = time.time() - self.globalStart
        self.log("Total time execution: {}".format(self.globalEnd))
        w, h = (63, 63)
        self.cache_image = cv2.cvtColor(self.cache_image, cv2.COLOR_BGR2RGB)
        for s in self.cache_count:
            for pt in self.cache_count[s]['matches']:
                cv2.rectangle(self.cache_image, pt, (pt[0] + w, pt[1] + h), self.colors[s], 2)
        cv2.imwrite('result.png', self.cache_image)

    def parse_response(self, data):
        data = data.replace(b'Give me the number of symbols separated by commas (e.g. 0,1,2,3,4,5)', b'')
        data = data.replace(b'\n', b'')

        data = re.sub(b'Good, you can continue!Base64 encoded image for challange #[0-9]+:', b'', data)
        data = re.sub(b'Well done! Next one.Base64 encoded image for challange #[0-9]+:', b'', data)
        return data


    def round(self, level):
        self.log("\nLevel #{}".format(level))
        # Receiving level banner
        banner = self.recvbanner(level)
        if banner is not False:
            # Receiving image
            data = self.recvuntil()
            # Timing
            self.tempEnd = time.time() - self.tempStart
            if (self.tempStart):
                self.log("Time from last reply: {}".format(self.tempEnd))

            # Timing from image response
            self.tempStart = time.time()

            self.log("Received image!")

            data = self.parse_response(data)
            # Saving image
            img = self.read_image(data, level)
            # Analyzing image
            reply = self.count_symbols(level, img)

            # Send reply
            self.send(reply)
            self.tempEnd = time.time() - self.tempStart
            self.log("Time for image analysis: {}".format(self.tempEnd))

            self.tempStart = time.time()
            self.round(level + 1)

    def first_round(self):
        # Sending captcha
        data = self.mainSocket.recv(8096).rstrip()
        data = data.replace(b'Provide a hex string X such that sha256(X)[-6:] = ', b'')
        cmd = b'grep ' + data + b'$ -m 1 ' + DICT
        hash = subprocess.run(cmd.split(b' '), stdout=subprocess.PIPE).stdout
        hash = hash.split(b':')[0]
        hash = binascii.hexlify(hash)
        self.send(hash)

        self.round(1)

    def start(self):
        self.init_recognition()
        self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainSocket.connect((HOST, PORT))
        self.first_round()

    def log(self, msg):
        print(msg)

    def end(self):
        self.log('End execution.')
        return False

s = Solver()
