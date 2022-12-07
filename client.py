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

def render(path: str, startFrame: int, endFrame: int):
    subprocess.run(f"blender -ba -f {startFrame}..{endFrame} {path}")

send(b"OK Server")