import os
import atexit
import socket
import sys
from traceback import format_exc
import shutil


dbpath = "./FSSDB"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 4626))
sock.listen()

def onexit():
    print("closing")
    sock.close()

atexit.register(onexit)

def touch(filename):
    f = open(filename, "x")
    f.close()

def find_nth_space(string, n):
    start = string.find(" ")
    while start >= 0 and n > 1:
        start = string.find(" ", start+1)
        n -= 1
    return start

def processreq(msg, sock):
    splmsg = msg.split()
    backmsg = "NORET"

    print(f"Command \"{msg}\" run.")

    # create dictionary
    if splmsg[0] == "CREATED":
        try:
            os.mkdir(os.path.join(dbpath, splmsg[1]))
        except FileExistsError:
            backmsg = "EXISTS"
    # delete dictionary
    elif splmsg[0] == "DELETED":
        try:
            shutil.rmtree(os.path.join(dbpath, splmsg[1]))
        except FileNotFoundError:
            backmsg = "DOESNOTEXIST"
    # write data point
    elif splmsg[0] == "WRITEP":
        try:
            f = open(os.path.join(dbpath, splmsg[1], splmsg[2]), "w")
            f.write(msg[find_nth_space(msg, 3) + 1:])
            f.close()
        except FileNotFoundError:
            backmsg = "DOESNOTEXIST"
    # delete data point
    elif splmsg[0] == "DELETEP":
        try:
            os.remove(os.path.join(dbpath, splmsg[1], splmsg[2]))
        except FileNotFoundError:
            backmsg = "DOESNOTEXIST"
    elif splmsg[0] == "READP":
        try:
            f = open(os.path.join(dbpath, splmsg[1], splmsg[2]), "r")
            backmsg = f.read()
            f.close()
        except FileNotFoundError:
            backmsg = "DOESNOTEXIST"
    # ping
    elif splmsg[0] == "PING":
        backmsg = "PONG"
    # powerdown
    elif splmsg[0] == "POWERDOWN":
        backmsg = "POWEROFF"
    else:
        backmsg = "COMMANDNOTFOUND"
    print(f"Response to client is \"{backmsg}\".")
    sock.send(backmsg.encode())
    if backmsg == "POWEROFF":
        sys.exit()


print("FSSDB server started.")


while True:
    clientsock, clientaddr = sock.accept()
    clientsock.settimeout(3)
    try:
        msg = clientsock.recv(1024).decode().strip()
        processreq(msg, clientsock)
    except SystemExit:
        sys.exit()
    except:
        print(format_exc())
    clientsock.close()