import socket
import threading
import traceback
import logging
import netaddr
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


def get_data(bytedata):
    action = bytedata[0]

    if action == 1:
        return registerClient(bytedata)
    else:
        return "Error"


def sendClientUpdate():
    for user in userList:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((user["ip"], user["port"]))
            message = pack("b6s", 2, "Update".encode())
            s.sendall(message)


def registerClient(bytedata):
    nnl = bytedata[1]
    new_format_string = 'b b s L I'.replace('s', str(nnl) + "s")

    try:
        temp_data = unpack(new_format_string, bytedata)
        temp_nickname = temp_data[2]
        temp_ip = temp_data[3]
        temp_port = temp_data[4]
        userList.append({'nick': str(temp_nickname), 'ip': str(netaddr.IPAddress(temp_ip)), 'port': temp_port})
        sendClientUpdate()
        print("Registered client!\n")
        print(userList)
    except Exception as e:  # Nicht schön, ich weiß, reicht aber für diesen Zweck aus
        print(e)
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
