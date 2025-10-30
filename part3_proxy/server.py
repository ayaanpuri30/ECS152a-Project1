import socket
import time

HOST = "127.0.0.1"
PORT = 7001 # must match what client sends via proxy
BACKLOG = 1
TIMEOUT = 10.0

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

def handle_message(msg):
    text = msg.strip()
    if text == "ping":
        return "pong\n"
    return ("echo: " + text + "\n")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(BACKLOG)
    print(f"SERVER- Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            conn.settimeout(TIMEOUT)
            try:
                raw = recv_until(conn)
                message = raw.decode("utf-8", errors="ignore").strip()
                if not message:
                    conn.sendall(b"")
                else:
                    reply = handle_message(message)
                    conn.sendall(reply.encode("utf-8"))
            except socket.timeout:
                pass
            finally:
                conn.close()
    finally:
        s.close()

if __name__ == "__main__":
    main()