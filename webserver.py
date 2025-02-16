#!/usr/bin/env python

import socket as s
import sys


def webserver(port: str | int =28333):
    socket = s.socket()
    socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    socket.bind(("", int(port)))
    socket.listen()
    print(f"Listening on locahost:{port}")
    while True:
        new_socket, addressinfo = socket.accept()
        print(f"Accepted connection from {addressinfo}...")
        buff = bytearray(1096)
        view = memoryview(buff)
        content = []
        while True:
            nbytes_recv = new_socket.recv_into(buff)
            if nbytes_recv == 0:
                break
            content.append(view[:nbytes_recv].tobytes().decode())
            if content[-1].endswith("\r\n\r\n"):
                break
        print(content)
        final_content = "".join(content)
        print(f"Received: {final_content}")

        # data = b""
        # while True:
        #     chunk = new_socket.recv(1096)
        #     if not chunk:
        #         break
        #     data += chunk
        #     if data.endswith(b"\r\n\r\n"):
        #         break

        # print(f"Received: {data.decode()}")

        txt = b"Hello, world"
        response = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(txt)}"
            "",
            "",
            txt.decode(),
        ]).encode()
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

