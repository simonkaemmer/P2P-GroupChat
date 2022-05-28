import socket
import threading
import traceback
import logging
from _thread import *
from struct import *

userList = []

nickname_len = 10
userlist_len = 10
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
        print(data)


def get_data(bytedata):
    action = bytedata[0]

    if action == 1:
        return registerClient(bytedata)
    else:
        return "Error"


def registerClient(bytedata):
    nnl = bytedata[1]
    new_format_string = 'b b s I I'.replace('s', str(nnl) + "s")

    try:
        temp_data = unpack(new_format_string, bytedata)
        temp_nickname = temp_data[2]
        temp_ip = temp_data[3]
        temp_port = temp_data[4]
        userList.append({'nick': temp_nickname, 'ip': temp_ip, 'port': temp_port})
    except Exception as e:    # Nicht schön, ich weiß, reicht aber für diesen Zweck aus
        logging.error(traceback.format_exc())

    return unpack(new_format_string, bytedata)


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


if __name__ == '__main__':
    Main()
