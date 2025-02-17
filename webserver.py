#!/usr/bin/env python

import socket as s
import sys


FORMAT = "ISO-8859-1"

def get_content_len(msg: str) -> int:
    parts = msg.split("\r\n")
    for p in parts:
        if p.lower().startswith("content-length"):
            return int(p.split(" ")[-1])
    return 0


def get_body(msg: str):
    parts = msg.split("\r\n\r\n")
    return parts[-1].strip()

def webserver(port: str | int =28333):
    socket = s.socket()
    socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    socket.bind(("", int(port)))
    socket.listen()
    print(f"Listening on localhost:{port}")
    while True:
        new_socket, addressinfo = socket.accept()
        print(f"Accepted connection from {addressinfo}...")

        buff = bytearray(1096)
        view = memoryview(buff)
        msg = []
        content_len = 0
        body = ""

        while True:
            if content_len > 0:
                body = get_body("".join(msg))
                if len(bytes(body, FORMAT)) == content_len:
                    break

            nbytes_recv = new_socket.recv_into(buff)
            if nbytes_recv == 0:
                break

            msg.append(view[:nbytes_recv].tobytes().decode(FORMAT))

            if content_len == 0:
                content_len = get_content_len("".join(msg))

            if msg[-1].endswith('\r\n\r\n'):
                break

        print(body)

        txt = b"Hello, world"
        response = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(txt)}"
            "",
            "",
            txt.decode(),
        ]).encode(FORMAT)
        new_socket.sendall(response)
        print("Response is sent...")
        new_socket.close()



def run_server():
    args = sys.argv[1:]
    if len(args) > 1:
        print(f"Usage: {sys.argv[0]} port")
        sys.exit(1)
    elif len(args):
        webserver(args[0])
    else:
        webserver()


if __name__ == "__main__":
    run_server()

