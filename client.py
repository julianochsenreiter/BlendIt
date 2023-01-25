import socket
import subprocess

MULTICAST_GROUP = '224.11.154.1'
PORT = 22333

# Time to live for packet
TTL = 2
cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def send(msg: bytes):
    print(f"Sending {str(msg)}...")
    cl.sendto(msg, (MULTICAST_GROUP, PORT))

def receive() -> bytes:
    return cl.recv(32)

def render(path: str, startFrame: int, endFrame: int):
    subprocess.run(f"blender -b {path} -o //render_ -f {startFrame}..{endFrame} -F PNG -x 1 ")

send(b"OK Server")

while True:
    msg = receive()
    