import socket
import struct

MULTICAST_GROUP = '224.11.154.1' # 224.B.l.1
PORT = 22333

serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serv.bind(('', PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # turn this into bytes
serv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print("BlendIt Server has started...")

while True:
    msg = serv.recv(1024)
    print(str(msg))