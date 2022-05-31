import socket
import threading
import traceback
import logging
import netaddr
from _thread import *
from struct import *

userList = []
packedUserList = []

nickname_len = 10
userlist_len = 10
f_string = 'b b s I I'  # Byte, Byte, string mit länge i, UnsignedInt, UnsignedInt
print_lock = threading.Lock()


# Fragen: Max len of nickanme?
# Byte-Anzahlen für die jeweiligen längen?

def recv_thread(c):
    while True:

        data = c.recv(1024)
        if not data:
            print_lock.release()
            break
        data = get_data(data)


def get_data(bytedata):
    action = bytedata[0]

    if action == 1:
        print("Action: Register")
        return registerClient(bytedata)
    elif action == 4:
        print("Action: registerBroadcast")
        print("UserList:" + str(userList))
        return registerBroadcast(bytedata)
    elif action == 6:
        print("Action: Deregister")
        return deregisterClient(bytedata)
    else:
        return "Error"


def deregisterClient(bytedata):
    nnl = bytedata[1]
    nick = str(unpack(f"bb{nnl}s", bytedata)[2]).replace("'", "").replace("b", "")
    for user in userList:
        if user["nick"] == nick:
            userList.remove(user)
            print(f"User with nick: {nick} logged out")
        else:
            print(f"User '{nick}' not found")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for user in userList:
            s.connect((user["ip"], user["port"]))
            message = pack(f"bb{nnl}s", 7, nnl, nick.encode())
            s.sendall(message)


def registerBroadcast(bytedata):
    bLen = bytedata[1]
    broadcast = str(unpack(f"bb{bLen}s", bytedata)[2]).replace("b", "").replace("'", "")
    print("BroadcastMessage: " + broadcast)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for user in userList:
            s.connect((user["ip"], user["port"]))
            message = pack(f"bb{bLen}s", 5, bLen, broadcast.encode())
            s.sendall(message)


# def sendUserList(ip, port):
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((ip, port))
#     packed_users = bytes()  # Only Users without ULL and Action-ID
#     ull = len(packedUserList)
#
#     for user in packedUserList:
#         print("Single User: " + str(unpack("" + str(len(user)) + "s", user)))
#         print("Single User: " + str(unpack("bb5sLI", user)))
#         print(str(unpack("15s", user[1:])))
#         if len(packed_users) == 0:
#             packed_users = user[1:]
#         else:
#             packed_users = packed_users + user[1:]
#
#     fully_packed_users = pack("bb", 2, ull) + packed_users  # bb b 5s L I
#     print("Fully Packed is : " + str(len(fully_packed_users)))
#     print(str(unpack("" + str(len(fully_packed_users)) + "s", fully_packed_users)))
#     print(str(unpack("bbb5sLI", fully_packed_users)))
#
#     s.sendall(fully_packed_users)


def sendClientUpdate(bytedata):
    for user in userList:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((user["ip"], user["port"]))
            nnl = bytedata[1]
            data = unpack("bb" + str(nnl) + "sLI", bytedata)
            message = pack("bb" + str(nnl) + "sLI", 3, nnl, data[2], data[3], data[4])
            s.sendall(message)


def registerClient(bytedata):
    if bytedata in packedUserList:
        return

    packedUserList.append(bytedata)
    nnl = bytedata[1]
    print("nicknamelen: " + str(nnl))
    new_format_string = 'b b s L I'.replace('s', str(nnl) + "s")
    print("Format-String:" + new_format_string)

    try:
        temp_data = unpack(new_format_string, bytedata)
        temp_nickname = temp_data[2]
        temp_ip = temp_data[3]
        temp_port = temp_data[4]
        userList.append(
            {'nick': str(temp_nickname).replace("b'", "").replace("'", ""), 'ip': str(netaddr.IPAddress(temp_ip)),
             'port': temp_port})
        sendClientUpdate(bytedata)
        # sendUserList(str(netaddr.IPAddress(temp_ip)), temp_port)
        print("Server: Registered client!\n")
        print("Server: " + str(userList))
    except Exception as e:  # Nicht schön, ich weiß, reicht aber für diesen Zweck aus
        print("Server: " + str(e))
        logging.error(traceback.format_exc())

    return


def Main():
    host = ""
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    s.listen(5)
    print("Server: Listening...")

    while True:
        c, addr = s.accept()

        print_lock.acquire(timeout=10.0)
        start_new_thread(recv_thread, (c,))


if __name__ == '__main__':
    Main()
