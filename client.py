import socket
import os 
import subprocess
import sys
from typing import Tuple

"""
    INIT
"""

# Connection info
MULTICAST_GROUP = '224.11.154.1'
PORT = 22333
hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)
TTL = 2

# Mount info
mount_point = "/etc/nfs"
file_extension = "*.blend"

# Create socket
cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

"""
    FUNCTIONS
"""
# Util functions
def log(msg: str):
    print(msg)

# Socket functions
def send(msg: bytes):
    log(f"Sending {str(msg)}...")
    cl.sendto(msg, (MULTICAST_GROUP, PORT))

def receivefile():
    subprocess.run(["mount", ipaddr + ":" + mount_point])
    # if os.path.exists(mount_point + "/" + file):
    #     subprocess.run(["cp", mount_point + "/" + file, file])

def receive() -> Tuple[bytes,str]:
    return cl.recvfrom(512)

# Render functions
def render(path: str, startFrame: int, endFrame: int):
    subprocess.run(f"blender -b {path} -o //render_ -f {startFrame}..{endFrame} -F PNG -x 1 ")


"""
    MAIN LOOP
"""

# Server information
server_address = ""
file_name = ""
frame_start = 0
frame_end = 0

wantsToExit = False

while not wantsToExit:
    if len(server_address) == 0:
        send(b"Hello")                
        msg, sender = receive()
        server_address = sender
        file_name = str(msg)

    if frame_start != frame_end:
        render(mount_point + file_name, frame_start, frame_end)
        send(b"DONE")
        
        frame_start = 0
        frame_end = 0

    msg, sender = receive()
    if sender != server_address:
        log("Other server tried to contact during session!")
        continue
    
    parts = str(msg).split(';')
    frame_start = int(parts[0])
    frame_end = int(parts[1])
    
