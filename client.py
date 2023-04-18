import asyncio
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
CLIENT_MOUNT_POINT = "/home/5ahitn/blenditfiles/"
MOUNT_POINT = "/var/blendit"
subprocess.run(["mkdir", "-p", CLIENT_MOUNT_POINT])


# Mount info
# mount_point = "/etc/nfs"
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

"""
Returns tuple of server and message as string
"""
async def findServer() -> Tuple[str, str]:
    send(b"HELLO")

    msg, sender = receive()
    return sender, str(msg)

def send(msg: bytes):
    log(f"Sending {str(msg)}...")
    cl.sendto(msg, (MULTICAST_GROUP, PORT))

def receive() -> Tuple[bytes,str]:
    print("receive")
    return cl.recvfrom(512)

def mountfile(server: str):
    print("mount file")
    subprocess.run(["mount", "-t", "nfs", f"{server}:{MOUNT_POINT}", CLIENT_MOUNT_POINT])

# Render functions
def render(path: str, startFrame: int, endFrame: int):
    log(f"render {path} {startFrame} {endFrame}")
    subprocess.run(f"blender -b {path} -o //render_ -f {startFrame}..{endFrame} -F PNG -x 1 ")


"""
    MAIN LOOP
"""

async def main():
    # Server information
    server_address = ""
    file_name = ""
    frame_start = 0
    frame_end = 0

    while True:
        if len(server_address) == 0:
            server_address, file_name = await findServer()
            mountfile(server_address)

        print("Server Found")
        if frame_start != frame_end:
            render(CLIENT_MOUNT_POINT + file_name, frame_start, frame_end)
            send(b"DONE")
            
            frame_start = 0
            frame_end = 0

        msg, sender = receive()
        if sender != server_address:
            log("Other server tried to contact during session!")
            continue
        print("received message")

        if msg == b"QUIT":
            quit()
        
        parts = str(msg).split(';')
        frame_start = int(parts[0])
        frame_end = int(parts[1])

def quit():
    subprocess.run(["umount", CLIENT_MOUNT_POINT])
    log("Finished all rendering, connection closed.")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())