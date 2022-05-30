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


def get_data(data):
    return unpack("b6s", data)


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
