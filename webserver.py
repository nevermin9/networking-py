#!/usr/bin/env python

import socket as s
import sys
import os


DEFAULT_PORT = 28333
FORMAT = "ISO-8859-1"
CRLF = "\r\n\r\n"
MIME = {
    ".txt": "text/plain",
    ".html": "text/html",
    "": "text/html",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg"
}

def get_content_len(msg: str) -> int:
    if not msg:
        return 0
    parts = msg.split("\r\n")
    for p in parts:
        if p.lower().startswith("content-length"):
            return int(p.split(" ")[-1])
    return 0


def get_body(msg: str)->str:
    if CRLF in msg:
        return msg.split(CRLF)[-1].strip()
    return ""


def get_headers(msg: str)->str:
    if CRLF in msg:
        return msg.split(CRLF)[0].strip()
    return ""


# def get_port(port: str)->int:
#     return int(port)


def create_webserver(port: int):
    server = s.socket()
    server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server.bind(("", int(port)))
    return server

def read_http_msg(socket: s.socket) -> tuple[str, str]:
    buff = bytearray(1096)
    view = memoryview(buff)
    msg: list[str] = []
    content_len = 0
    body = ""
    headers = ""

    while True:
        if content_len > 0:
            body = get_body("".join(msg));
            if len(bytes(body, FORMAT)) == content_len:
                break

        nbytes_recv = socket.recv_into(buff)

        if nbytes_recv == 0:
            break

        msg.append(view[:nbytes_recv].tobytes().decode(FORMAT))
        headers = get_headers("".join(msg))

        if content_len == 0:
            content_len = get_content_len(headers)

        if msg[-1].endswith(CRLF) and headers and content_len == 0:
            break

    return (headers, body)

def read_file(filename: str) -> bytes:
    file_ext = os.path.splitext(filename)[-1]
    path_to_file = ""
    if not file_ext:
        path_to_file = f"./static/{filename}.html"
    else:
        path_to_file = f"./static/{filename}"

    try:
        with open(path_to_file, mode="rb") as f:
            data = f.read()
            return data
    except:
        return b""
    
def not_found():
    return "\r\n".join([
        "HTTP/1.1 404 Not Found",
        "",
        "",
    ]).encode(FORMAT)

def hello_world():
    txt = b"Hello, world"
    return "\r\n".join([
        "HTTP/1.1 200 OK",
        "Content-Type: text/plain",
        f"Content-Length: {len(txt)}"
        "",
        "",
        txt.decode(),
    ]).encode(FORMAT)


def accept_connections(server: s.socket):
    while True:
        socket, addressinfo = server.accept()
        print(f"Accepted connection from {addressinfo}...")

        headers, body = read_http_msg(socket)
        # print(f"Headers: {headers}")
        # print(f"Body: {body}")

        request_line = headers.split("\r\n")[0]
        method, resource_path, http_v = request_line.split()
        print(f"{ method } {resource_path} {http_v}")

        if method != "GET" or resource_path == "/favicon.ico":
            socket.sendall(not_found())
            socket.close()
            continue

        file_name = os.path.split(resource_path)[-1]

        if not file_name:
            socket.sendall(hello_world())
            socket.close()
            continue


        file_content = read_file(file_name)

        if not file_content:
            socket.sendall(not_found())
            socket.close()
            continue

        mime_type = MIME[os.path.splitext(file_name)[-1]]
        content_len = len(file_content)

        response = "\r\n".join([
            "HTTP/1.1 200 OK",
            f"Content-Type: {mime_type}",
            f"Content-Length: {content_len}"
            "",
            "",
            file_content.decode(),
        ]).encode(FORMAT)
        socket.sendall(response)
        socket.close()



def webserver(port: int):
    server = create_webserver(port)
    server.listen()
    print(f"Listening on localhost:{port}")
    accept_connections(server)


def run_server():
    args = sys.argv[1:]
    if len(args) > 1:
        print(f"Usage: {sys.argv[0]} port")
        sys.exit(1)
    port = int(*args[:1] or [DEFAULT_PORT])
    webserver(port)



if __name__ == "__main__":
    run_server()

