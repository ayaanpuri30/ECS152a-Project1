import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
SENTINEL = b"__END__"

CHUNK_SIZE = 32 * 1024 # 32 KB per packet
TOTAL_BYTES = 100 * 1024 * 1024 # 100 MB total to send
RECV_TIMEOUT = 10.0 # seconds

def main():
    # UDP socket creation
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (SERVER_HOST, SERVER_PORT)

    chunk = b"x" * CHUNK_SIZE # chunk sized x's
    bytes_sent = 0

    print(f"Sending {TOTAL_BYTES} bytes to {SERVER_HOST}:{SERVER_PORT}...")

    # send exactly TOTAL_BYTES in CHUNK_SIZE pieces
    while bytes_sent < TOTAL_BYTES:
        remaining = TOTAL_BYTES - bytes_sent
        if remaining >= CHUNK_SIZE:
            to_send = chunk
        else:
            to_send = b"x" * remaining

        client_socket.sendto(to_send, server_address)
        bytes_sent += len(to_send)

    # tell server done
    client_socket.sendto(SENTINEL, server_address)
    print("finished sending all data. ")

    # get throughput result from server
    client_socket.settimeout(RECV_TIMEOUT)
    try:
        data, _ = client_socket.recvfrom(1024)
        result = data.decode("ascii", errors="ignore")
        print(f"Throughput reported by server: {result} KB/s")
    except socket.timeout:
        print("Timed out waiting for server")

    client_socket.close()
    print("Client closed.")

if __name__ == "__main__":
    main()