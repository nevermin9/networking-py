#!/usr/bin/env python
import sys
import socket as s

FORMAT = "ISO-8859-1"
def webclient(host: str, port: str | int =80):
    p = int(port)
    socket = s.socket()
    print(f"making request to {host, p}...")
    socket.connect((host, p))
    payload = b'How are you doing, man?'
    http_message = "\r\n".join([
        "POST / HTTP/1.1",
        f"Host: {host}",
        "Connection: close",
        "Content-Type: text/plain",
        f"Content-Length: {len(payload)}",
        "",
        payload.decode(),
    ])
    socket.sendall(http_message.encode(FORMAT))
    buff_size = 1096
    res = socket.recv(buff_size)
    while len(res):
        print(res.decode(FORMAT))
        res = socket.recv(buff_size)
    print("-finsih-")


def run_client():
    args = sys.argv[1:]
    if 0 < len(args) < 3:
        webclient(*args)
    else:
        print(f"Usage: {sys.argv[0]} host [port]")
        sys.exit(1)

if __name__ == "__main__":
    run_client()



