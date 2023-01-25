import socket
import struct
import os
import subprocess
import sys
import pyfiglet

"""
    INIT
"""

# Setup connection Info
MULTICAST_GROUP = '224.11.154.1' # 224.B.l.1
PORT = 22333

# Setup mount info
mount_point = "/mnt/nfs"
FILE_PATH = sys.argv[1]

# Create socket
serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind(('', PORT))
# Enable multicast
mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # turn this into bytes
serv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

WELCOME_TEXT = pyfiglet.figlet_format("BLENDIT")
print(WELCOME_TEXT)
print("BlendIT server has started...")

registered_clients = list()

"""
    FUNCTIONS
"""

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
        subprocess.run(["cp", FILE_PATH, mount_point])

"""
    MAIN LOOP
"""

while True:
    handleMessage(serv.recvfrom(1024))
    transferFile()





    
