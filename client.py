import socket
import sys

sock = None



while True:
    inp = input(" >>")
    if inp == "CLOSE":
        sys.exit()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20)
    sock.connect(("127.0.0.1", 4626))
    sock.send(inp.encode())
    print(sock.recv(1024).decode())
    sock.close()