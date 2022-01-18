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

    def terminate(self):
        self.socket.close()
        os.kill(os.getpid(), signal.SIGINT)


    def remove_current_command(self):
        print('\b'*(len(self.cur)), end='', flush=True)

    def print_current_command(self):
        print(f'{self.cur}', end='', flush=True)

    def handle_reader(self, reader):

        if reader == self.socket:
            data = reader.recv(1024)
            if len(data) == 0:
                self.terminate()
            text = data.decode('UTF-8')
            self.remove_current_command()
            print(f'{text}', end='', flush=True)
            self.print_current_command()

        if reader == sys.stdin:
            c = sys.stdin.read(1)
            if ord(c) == 3:
                self.terminate()
            if ord(c) == 13:
                print(f'\n\r', end='', flush=True)
                if self.cur == 'quit':
                    self.terminate()
                    
                self.socket.send(self.cur.encode('UTF-8'))
                self.cur = ''
            else:
                print(c, end='', flush=True)
                self.cur += c

    def run(self):
        try:
            while True:
                readers, _, _ = select(self.readable, [], [], 0.1)
                [ self.handle_reader(r) for r in readers ]
        except:
            self.terminate()
