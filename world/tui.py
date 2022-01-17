import sys
import signal
import os
from select import select
import time
import socket

class Tui():
    def __init__(self, s):
        self.socket = s
        self.cur = ''
        self.interupted = True
        self.readable = set()
        self.readable.add(sys.stdin)
        self.readable.add(self.socket)
        self.writable = set()

    def run(self):
        try:
            print('> ', end='', flush=True)
            while True:
                readers, _, _ = select(self.readable, [], [], 0.1)
                for reader in readers:
                    if reader == self.socket:
                        data = reader.recv(1024)
                        if len(data) == 0:
                            os.kill(os.getpid(), signal.SIGINT)
                        text = data.decode('UTF-8')
                        print('\b'*(len(self.cur)+2), end='', flush=True)
                        print(f'{text}{chr(13)}{chr(10)}', end='', flush=True)
                        print(f'> {self.cur}', end='', flush=True)
                    if reader == sys.stdin:
                        c = sys.stdin.read(1)
                        if ord(c) == 3:
                            os.kill(os.getpid(), signal.SIGINT)
                        if ord(c) == 13:
                            print(f'{chr(13)}{chr(10)}> ', end='', flush=True)
                            if self.cur == 'quit':
                                self.socket.close()
                                os.kill(os.getpid(), signal.SIGINT)

                            self.socket.send(self.cur.encode('UTF-8'))
                            self.cur = ''
                        else:
                            print(c, end='', flush=True)
                            self.cur += c
        except:
            os.kill(os.getpid(), signal.SIGINT)
