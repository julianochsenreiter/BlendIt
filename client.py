import socket
import os 
import subprocess
import sys

MULTICAST_GROUP = '224.11.154.1'
PORT = 22333
mount_point = "/etc/nfs"
hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)
file = "*.blend"


# Time to live for packet
TTL = 2
cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def send(msg: bytes):
    print(f"Sending {str(msg)}...")
    cl.sendto(msg, (MULTICAST_GROUP, PORT))

send(b"OK Server")

def reveivefile():
    subprocess.run(["mount", ipaddr + ":" + mount_point])
    if os.path.exists(mount_point + "/" + file):
        subprocess.run(["cp", mount_point + "/" + file, file])