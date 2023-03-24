import socket
import struct
import os
import subprocess
import sys
from typing import Tuple
import pyfiglet
import asyncio

"""
    INIT
"""
if len(sys.argv) < 2:
    print("You need to specify a .blend file to render!")
    sys.exit(1)

if os.getuid() != 0:
    print("")

# Setup connection Info
MULTICAST_GROUP = '224.11.154.1' # 224.B.l.1
PORT = 22333
framesdict = {}

# Setup mount info
MOUNT_POINT = "./data"
CLIENT_MOUNT_POINT = "var/blendit/"
filePath = sys.argv[1]

# Create socket
serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind((MULTICAST_GROUP, PORT))

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

# Render functions
def getFrameLength() -> int: 
    output = subprocess.check_output(["blender", "-b", filePath , "-P", "./getdata.py"])
    frames = str.split(str(output), "\\r")[0].removeprefix("b'")
    print(f"Output: {frames}")

    return int(frames)

def calculateFrameRange() -> Tuple[int, int]:
    frames = getFrameLength()
    perclient = frames / registered_clients.count
    end = 0
    while (end < frames):
        start = end
        end += perclient
        if end > frames:
            end = frames
        start_frame = start
        end_frame = end

        for client in registered_clients:
            framesdict[client] = (start_frame, end_frame)


    return start_frame, end_frame

# Socket functions
def receive() -> Tuple[bytes, str]:
    return serv.recvfrom(512)

async def handleMessage(msg, sender):
    cl = sender[0] # get IP address from sender tuple
    print(f"Recieved {msg} from {sender}")

    if cl not in registered_clients:
        print("New client, adding to list")
        registered_clients.append(cl)
        transferFile(sender)
    else:
        print("Client is known!")
    


def transferFile(client: str):
    

    address = client[0]
    subprocess.run(["mount", "-t", "nfs", f"{address}:{CLIENT_MOUNT_POINT}", MOUNT_POINT])
    subprocess.run(["cp", filePath, MOUNT_POINT])

    serv.sendto(bytes(f"{filePath}{MOUNT_POINT}", encoding="UTF8"), client)

def sendFrameRange(client: str, start: int, end: int):
    serv.sendto(f"{start};{end}",client)

"""
    MAIN LOOP
"""

def main():
    while True:
        msg, sender = receive()
        asyncio.run(handleMessage(msg, sender))
        


if __name__ == "__main__":
    main()


    
