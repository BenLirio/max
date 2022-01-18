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

debug = True
save = True
def log(s):
    if debug:
        print(s, end=f'{chr(13)}{chr(10)}')

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

class Message():
    def __init__(self, text, broadcast=False):
        self.text = text
        self.broadcast = broadcast

class Client():
    def __init__(self, state):
        self.context = 'get_username'
        self.state = state
        self.username = ''


    def update(self, text):
        if self.context == 'get_username':
            if text in self.state.users:
                self.username = text
                self.context = 'get_password'
                return Message('Password: ')
            else:
                return Message('Username: ')
        elif self.context == 'get_password':
            if text == self.state.users[self.username].password:
                self.context = 'default'
                return Message(f'Welcome {self.username}\n\r')
            else:
                self.context = 'get_username'
                return Message(f'Wrong password.\n\rUsername: ')
        elif self.context == 'default':
            words = text.split(' ')
            user = self.state.users[self.username]
            location = self.state.locations[user.location]
            if text == 'look':
                return Message(location.name)
            if words[0] == 'say':
                return Message(f'{user.name}: {" ".join(words[1:])}\n\r', broadcast=True)
        return Message('Unmatched\n\r')


class ServerThread(Thread):
    def __init__(self, address, exit_signal, ready_signal):
        self.exit_signal = exit_signal
        Thread.__init__(self)
        self.socket = socket()
        self.socket.bind(address)
        self.socket.listen()
        ready_signal.set()
        self.clients = {}
        self.load_state()

    def send(self, client_socket, text):
        client_socket.send(text.encode('UTF-8'))
    def broadcast(self, text):
        [self.send(cs, text) for cs in self.clients]

    def read(self, client_socket):
        return client_socket.recv(1024).decode('UTF-8')

    def handle_reader(self, reader):
        if reader == self.socket:
            client_socket,_ = self.socket.accept()
            client_socket.send('Username: '.encode('UTF-8'))
            client = Client(self.state)
            self.clients[client_socket] = client
        else:
            client_id = reader
            text = self.read(client_id)
            if len(text) == 0:
                del self.clients[client_id]
            else:
                client = self.clients[client_id]
                message = client.update(text)
                if message.broadcast:
                    self.broadcast(message.text)
                else:
                    self.send(client_id, message.text)

    def load_state(self):
        if save and os.path.exists('state.pkl'):
            with open('state.pkl', 'rb') as p:
                self.state = pickle.load(p)
        else:
            self.state = State()

    def save_state(self):
        if save:
            with open('state.pkl', 'wb') as p:
                pickle.dump(self.state, p, pickle.HIGHEST_PROTOCOL)

    def run(self):
        while True:
            if self.exit_signal.is_set():
                self.save_state()
                break
            readable = list(self.clients)
            readable.append(self.socket)

            readers, _, _ = select(readable, [], [], 0.1)
            [self.handle_reader(r) for r in readers]
