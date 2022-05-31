import socket
import time
import threading
from _thread import *
import netaddr
from struct import *

server_ip = "127.0.0.1"
server_port = 5000
race_lock = threading.Lock()
userList = []

ownPort = 5004


def recv_thread(c):
    while True:
        data = c.recv(1024)
        if not data:
            race_lock.release()
            break
        data = get_data(data)


def send_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Client: Sendthread running")
    s.connect((server_ip, server_port))

    register(s)
    time.sleep(2)
    regBroadcast(s)
    time.sleep(2)
    deregister(s, "Tanja")
    time.sleep(2)
    deregister(s, "Kurt")

def udp_thread():
    UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPSocket.bind(("127.0.0.1", 20002))
    while(True):
        bytes = UDPSocket.recvfrom(1024)
        message = bytes[0]
        address = bytes[1]

def register(s):
    # Register
    nick = "Sabine"
    message = pack(f'b b {str(len(nick))}s L I', 1, len(nick), nick.encode(), netaddr.IPAddress("127.0.0.1"), ownPort)
    s.sendall(message)


def regBroadcast(s):
    # Register Broadcast
    broadcast = "Hello World"
    message = pack(f"bb{str(len(broadcast))}s", 4, len(broadcast), broadcast.encode())
    s.sendall(message)


def deregister(s, user):
    nick = user
    message = pack(f"bb{str(len(nick))}s", 6, len(nick), nick.encode())
    s.sendall(message)
    print("UserList:" + str(userList))


def get_data(bytedata):
    action = bytedata[0]

    if action == 2:
        ull = bytedata[1]  # b b b 4s L I
        print("Ull: " + str(ull))

        for x in range(2, len(bytedata)):
            nnl = bytedata[x]
            print("nickname-length: " + str(nnl))
            nick = unpack("" + str(nnl) + "s", bytedata[x: x + nnl + 1])
            ip = unpack("L", bytedata[x + nnl + 1: x + nnl + 2])
            port = bytedata[x + nnl + 2: x + nnl + 2 + 1]
            print("Nick: " + str(nick) + " ip: " + str(ip) + " port: " + port)

        return ""
    elif action == 3:
        nnl = bytedata[1]
        user = unpack(f"bb{nnl}sLI", bytedata)
        userList.append({'nick': str(user[2]).replace("b'", "").replace("'", ""), 'ip': str(netaddr.IPAddress(user[3])),
                         'port': user[4]})
        print("UserList in Client: " + str(userList))

    elif action == 5:
        bcl = bytedata[1]
        data = str(unpack(f"bb{bcl}s", bytedata)[2]).replace("'", "").replace("b", "")
        print("Broadcast: " + data)
    elif action == 7:
        print("UserList:" + str(userList))
        nnl = bytedata[1]
        nick = str(unpack(f"bb{nnl}s", bytedata)[2]).replace("'", "").replace("b", "")
        for user in userList:
            if user["nick"] == nick:
                userList.remove(user)
                print(f"User with nick: {nick} logged out")
            else:
                print(f"User '{nick}' not found")
    else:
        return "Error"


def Main():
    print("Main running")
    start_new_thread(send_thread, ())
    start_new_thread(udp_thread, ())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", ownPort))
    s.listen(5)

    while True:
        c, addr = s.accept()
        race_lock.acquire(timeout=10.0)
        start_new_thread(recv_thread, (c,))

    input("Press enter to interrupt!")


if __name__ == '__main__':
    Main()
