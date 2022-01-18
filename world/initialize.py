import sys
import termios
import signal
import tty

class Environment():
    def __init__(self, exit_signal, client_socket, threads):
        self.exit_signal = exit_signal
        self.client_socket = client_socket
        self.threads = threads
        self.configure_terminal()

        signal.signal(signal.SIGINT, self.sigint_handler)

    def configure_terminal(self):
        fd = sys.stdin.fileno()
        self.old_terminal_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
        except:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print('Failed to configure terminal')
            sys.exit(1)

    def sigint_handler(self, signum, frame):
        self.exit_signal.set()
        self.client_socket.close()
        for td in self.threads:
            td.join()
        self.revert_terminal()
        sys.exit(1)

    def revert_terminal(self):
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, self.old_terminal_settings)

