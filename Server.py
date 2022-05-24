import socket
import threading
from _thread import *
from struct import *

nickname_len = 10
userlist_len = 10
format_strings = ['b b s I I', '', '']
f_string = 'b b s I I'  # Byte, Byte, string mit länge i, UnsignedInt, UnsignedInt
print_lock = threading.Lock()


# Fragen: Max len of nickanme?
# Byte-Anzahlen für die jeweiligen längen?

def thread(c):
    while True:

        data = c.recv(1024)
        if not data:
            print_lock.release()
            break
        data = get_data(data)


def get_data(bytedata, action):
    n = unpack(format_strings[action], bytedata)
    n =


def Main():
    host = ""
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    s.listen(5)
    print("Listening...")

    while True:
        c, addr = s.accept()

        print_lock.acquire(timeout=10.0)
        print("Connected to : ", addr[0], ":", addr[1])
        start_new_thread(thread, (c,))
