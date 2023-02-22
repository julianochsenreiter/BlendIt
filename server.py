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
if sys.argv.count < 2:
    print("You need to specify a .blend file to render!")
    sys.exit(1)

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

# Render functions
def getFrameLength() -> int: 
    output = subprocess.check_output(["blender", "-b", FILE_PATH , "-P", "./getdata.py"])
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
    return start, end

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
    subprocess.run(["mount", client + ":" + mount_point])
    subprocess.run(["cp", FILE_PATH, mount_point])

    serv.sendto(mount_point + FILE_PATH)

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


    
