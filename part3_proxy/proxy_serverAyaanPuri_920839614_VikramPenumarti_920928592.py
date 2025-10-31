import socket
import json

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 6001
BACKLOG = 1
TIMEOUT = 10.0
BLOCKLIST_FILE = "blocklist.txt" # one IP per line

def load_blocklist(path):
    blocked = set()
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                blocked.add(line)
    except FileNotFoundError:
        pass
    return blocked

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

def handle_client(client_sock, blocklist):
    # 1. receive one JSON line from client
    raw = recv_until(client_sock)
    if not raw:
        client_sock.sendall(b"Error\n")
        return

    try:
        payload = json.loads(raw.decode("utf-8", errors="ignore"))
        server_ip = payload.get("server_ip")
        server_port = int(payload.get("server_port", 0))
        message = payload.get("message", "")

        # validation
        if not server_ip or server_port <= 0 or not isinstance(message, str):
            client_sock.sendall(b"Error\n")
            return
    except Exception:
        client_sock.sendall(b"Error\n")
        return

    # 2. blocklist check
    if server_ip in blocklist:
        client_sock.sendall(b"Error\n")
        return

    # 3. connect to destination server and send message
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as upstream:
            upstream.settimeout(TIMEOUT)
            upstream.connect((server_ip, server_port))

            to_send = (message.strip() + "\n").encode("utf-8")
            upstream.sendall(to_send)

            reply = recv_until(upstream)
            if not reply:
                client_sock.sendall(b"Error\n")
            else:
                client_sock.sendall(reply)
    except Exception:
        try:
            client_sock.sendall(b"Error\n")
        except Exception:
            pass

def main():
    blocklist = load_blocklist(BLOCKLIST_FILE)
    print(f"PROXY- Loaded blocklist: {blocklist}" if blocklist else "PROXY- No blocklist entries")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((PROXY_HOST, PROXY_PORT))
    s.listen(BACKLOG)
    print(f"PROXY- Listening on {PROXY_HOST}:{PROXY_PORT}")

    try:
        while True:
            client, addr = s.accept()
            client.settimeout(TIMEOUT)
            try:
                handle_client(client, blocklist)
            finally:
                client.close()
    finally:
        s.close()

if __name__ == "__main__":
    main()
