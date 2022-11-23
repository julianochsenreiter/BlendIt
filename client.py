import socket

MULTICAST_GROUP = '224.11.154.1'
PORT = 22333

# Time to live for packet
TTL = 2
cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def send(msg: bytes):
    print(f"Sending {str(msg)}...")
    cl.sendto(msg, (MULTICAST_GROUP, PORT))

send(b"OK Server")