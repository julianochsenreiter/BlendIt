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

# Setup mount info
MOUNT_POINT = "/var/blendit"
subprocess.run(["mkdir", "-p", MOUNT_POINT])
filePath = sys.argv[1]
framerate = 60
if len(sys.argv) < 3:
    framerate = int(sys.argv[2])

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

framedict = {}


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
    
    start_frame = framedict[max(framedict)]
    end_frame = start_frame + perclient
    if end_frame > frames:
        end_frame = frames

    if start_frame > frames:
        return (-1, -1)

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

    elif msg == b"DONE":
       start_frame, end_frame = framedict[cl]
       print(f"Client {cl} finished frames {start_frame}-{end_frame}, assigning new frame range")
       updateClientFrameRange(sender) 

    else:
        print("Client is known!")

def transferFile(client: str):
    subprocess.run(["cp", filePath, MOUNT_POINT])
    serv.sendto(bytes(f"{filePath}{MOUNT_POINT}", encoding="UTF8"), client)

def sendFrameRange(client: str, start: int, end: int):
    serv.sendto(bytes(f"{start};{end}", encoding="UTF8"),client)

def combineImages():
    print("Combining images...")
    subprocess.run(["ffmpeg", "-framerate", str(framerate), "-pattern_type", "glob",  "-i", MOUNT_POINT + "'*.png'", "render.mp4"])

"""
    MAIN LOOP
"""

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(receiveLoop())
    loop.create_task(distributeFrames())
    loop.run_forever()


async def receiveLoop():
    while True:
        msg, sender = receive()
        await handleMessage(msg, sender)

async def distributeFrames():
    while True:
        allInvalid = True
        for client in registered_clients:
            if not client in framedict:
                await updateClientFrameRange(client)
                allInvalid = False
            elif framedict[client]:
                allInvalid = False
            else:
                print(f"{client} vs {registered_clients}")
        
        if allInvalid:
            quit()
        

async def updateClientFrameRange(client: str):
    print(f"updateClientFrameRange {client}")
    frame_start, frame_end = calculateFrameRange()
    if frame_start == -1:
        framedict[client] = (-1,-1)
    else:
        framedict[client] = (frame_start, frame_end)
        sendFrameRange(client, frame_start, frame_end)
    

def quit():
    for client in registered_clients:
        serv.sendto(b"QUIT", client)

    print("Done rendering")
    combineImages()
    print("Done combining images")

    sys.exit(0)

if __name__ == "__main__":
    main()


    
