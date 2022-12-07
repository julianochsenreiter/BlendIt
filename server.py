import socket
import struct
import os
import subprocess
import sys

MULTICAST_GROUP = '224.11.154.1' # 224.B.l.1
PORT = 22333
mount_point = "/mnt/nfs"

serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serv.bind(('', PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # turn this into bytes
serv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print("BlendIt Server has started...")

registered_clients = list()

def handleMessage(msg, sender):
    cl = sender[0] # get IP address from sender tuple
    print(f"Recieved {msg} from {sender}")

    if cl not in registered_clients:
        print("New client, adding to list")
        registered_clients.append(cl)
    else:
        print("Client is known!")

def transferFile():
    for client in registered_clients:
        subprocess.run(["mount", client + ":" + mount_point])
        subprocess.run(["cp", sys.argv[1], mount_point])
while True:
    handleMessage(serv.recvfrom(1024))





    
