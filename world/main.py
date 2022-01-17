import random
import asyncio
import pickle
from socket import socket
from threading import Thread, Event, Lock
from select import select
import sys
import signal
import time
import tty
import termios
import readchar
import os
from tui import Tui


debug = True
save = True
address = ('0.0.0.0', random.randint(0,1000)+3000)
address = ('0.0.0.0', 3001)

done = Event()
server_ready = Event()
threads = []
clients = set()
clients_lock = Lock()

def log(s):
    if debug:
        print(s, end=f'{chr(13)}{chr(10)}')


def initialize():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
    except:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.exit(1)
    def sigint_handler(signum, frame):
        done.set()
        s.close()
        for td in threads:
            td.join()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.exit(1)
    signal.signal(signal.SIGINT, sigint_handler)


"""
Server
"""
class User():
    def __init__(self):
        pass
state_lock = Lock()


class Command():
    def __init__(self, text):
        pass


class User():
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.location = 'lobby'

class Location():
    def __init__(self, name, description):
        self.name = name
        self.description = description
class State():
    def __init__(self):
        self.users = {
                'max': User('max', 'max'),
                'ben': User('ben', 'ben')
        }
        self.locations = {
                'lobby': Location('lobby', 'this is the lobby')
        }

class Client():
    def __init__(self, socket, state):
        self.socket = socket
        self.socket.send('Username:'.encode('UTF-8'))
        self.context = 'get_username'
        self.state = state
        self.username = ''

    def send(self, text):
        self.socket.send(text.encode('UTF-8'))

    def update(self, text):
        if self.context == 'get_username':
            if text in self.state.users:
                self.username = text
                self.context = 'get_password'
                return 'Password:', ''
            else:
                self.send('Username:')
        elif self.context == 'get_password':
            if text == self.state.users[self.username].password:
                self.context = 'default'
                return f'Welcome {self.username}', ''
            else:
                self.context = 'get_username'
                return f'Wrong password.\nUsername:', ''
        elif self.context == 'default':
            words = text.split(' ')
            user = self.state.users[self.username]
            location = self.state.locations[user.location]
            if text == 'look':
                self.send(location.name)
                return location.name, ''
            if words[0] == 'say':
                return '', f'{user.name}: {" ".join(words[1:])}'
        return 'Unmatched', ''


class ServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = socket()
        self.socket.bind(address)
        self.socket.listen()
        log('Server created')
        server_ready.set()
        self.clients = set()
        if save and os.path.exists('state.pkl'):
            with open('state.pkl', 'rb') as p:
                self.state = pickle.load(p)
        else:
            self.state = State()
    def handle_reader(self, reader):
        if reader == self.socket:
            client_socket,_ = self.socket.accept()
            client = Client(client_socket, self.state)
            self.clients.add(client)
        else:
            for cs, client in [(c.socket, c) for c in self.clients]:
                if cs == reader:
                    data = reader.recv(1024)
                    if len(data) == 0:
                        self.clients.remove(client)
                    else:
                        text = data.decode('UTF-8')
                        res, res_all = client.update(text)
                        if len(res) > 0:
                            client.send(res)
                        if len(res_all) > 0:
                            for client in self.clients:
                                client.send(res_all)
    def run(self):
        while True:
            if done.is_set():
                if save:
                    with open('state.pkl', 'wb') as p:
                        pickle.dump(self.state, p, pickle.HIGHEST_PROTOCOL)
                break
            readable = [c.socket for c in self.clients]
            readable.append(self.socket)

            readers, _, _ = select(readable, [], [], 0.1)
            [self.handle_reader(r) for r in readers]

""" 
Local
"""
initialize()
s = socket()
try:
    s.connect(address)
except:
    serverThread = ServerThread()
    serverThread.start()
    threads.append(serverThread)
    server_ready.wait()
    s.connect(address)



tui = Tui(s)
tui.run()
