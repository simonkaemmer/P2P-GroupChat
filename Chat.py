import socket
from struct import *

HOST = "127.0.0.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    message = pack('b b 4s I I', 1, 4, "Dani".encode(), 2130706433, 5000)
    s.sendall(message)
    print("Data sent!")
