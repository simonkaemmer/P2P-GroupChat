import socket
import threading
from _thread import *
import netaddr
from struct import *

server_ip = "127.0.0.1"
server_port = 5000
race_lock = threading.Lock()


def recv_thread(c):
    while True:
        data = c.recv(1024)
        if not data:
            race_lock.release()
            break
        data = get_data(data)
        print("Client: " + str(data))


def send_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Client: Sendthread running")
    s.connect((server_ip, server_port))
    message = pack('b b 5s L I', 1, 5, "Tanja".encode(), netaddr.IPAddress("127.0.0.1"), 5001)
    s.sendall(message)
    print("Client: Data sent!")


def get_data(bytedata):
    action = bytedata[0]

    if action == 2:
        ull = bytedata[1]  # b b b 4s L I
        print("Ull: " + str(ull))

        for x in range(2, len(bytedata)):
            nnl = bytedata[x]
            print("nickname-length: " + str(nnl))
            nick = unpack("" + str(nnl) + "s", bytedata[x: x + nnl+1])
            ip = unpack("L", bytedata[x + nnl+1: x + nnl + 2])
            port = bytedata[x + nnl + 2: x + nnl + 2 + 1]
            print("Nick: " + str(nick) + " ip: " + str(ip) + " port: " + port)

        return "Working"
    else:
        return "Error"


def Main():
    print("Main running")
    start_new_thread(send_thread, ())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 5001))
    s.listen(5)

    while True:
        c, addr = s.accept()
        race_lock.acquire(timeout=10.0)
        start_new_thread(recv_thread, (c,))

    input("Press enter to interrupt!")


if __name__ == '__main__':
    Main()
