import socket
import json

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 6001
TIMEOUT = 10.0

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7001
MESSAGE = "ping"

def recv_until(sock, delim=b"\n"):
    data = b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
        if delim in data:
            break
    return data

def main():
    payload = {
        "server_ip": SERVER_IP,
        "server_port": SERVER_PORT,
        "message": MESSAGE
    }
    body = (json.dumps(payload) + "\n").encode("utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect((PROXY_HOST, PROXY_PORT))

    s.sendall(body)
    reply = recv_until(s)
    s.close()

    text = reply.decode("utf-8", errors="ignore").strip()
    print("CLIENT- Proxy returned:", text)

if __name__ == "__main__":
    main()
