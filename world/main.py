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
from server import ServerThread
from initialize import Environment


address = ('0.0.0.0', random.randint(0,1000)+3000)
address = ('0.0.0.0', 3001)

exit_signal = Event()
ready_signal = Event()
threads = []

client_socket = socket()

env = Environment(exit_signal, client_socket, threads)

try:
    client_socket.connect(address)
except:
    serverThread = ServerThread(address, exit_signal, ready_signal)
    serverThread.start()
    threads.append(serverThread)
    ready_signal.wait()
    client_socket.connect(address)



tui = Tui(client_socket)
tui.run()
