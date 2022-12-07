import socket
import struct

MULTICAST_GROUP = '224.11.154.1' # 224.B.l.1
PORT = 22333

serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serv.bind(('', PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # turn this into bytes
serv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print("BlendIt Server has started...")

registered_clients = list()

def handleMessage(msg, sender):
    cl = sender[0] # get IP address from sender tuple
    print(f"Recieved {msg} from {sender}")

    if cl not in registered_clients:
        print("New client, adding to list")
        registered_clients.append(cl)
    else:
        print("Client is known!")

while True:
    handleMessage(serv.recvfrom(1024))
    
