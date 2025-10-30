import socket
import time

# server config
HOST = "127.0.0.1"
PORT = 9000
BUFFER_SIZE = 65535 # max UDP payload size
SENTINEL = b"__END__" # final message from client
TIMEOUT = 10.0

# UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(TIMEOUT)

print(f"Server on {HOST}:{PORT}")

total_bytes = 0
start_time = None
client_address = None

while True:
    try:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
    except socket.timeout:
        print("No data received.")
        break

    client_address= addr

    # first data packet -> start the timer
    if start_time is None and data != SENTINEL:
        start_time = time.perf_counter()

    # last packet -> stop
    if data == SENTINEL:
        break

    total_bytes += len(data)

# calculate only if data
if start_time is not None:
    end_time = time.perf_counter()
    duration = end_time - start_time
    if duration <= 0:
        duration = 1e-12

    # convert to KBs (1024 bytes)
    throughput = (total_bytes / 1024.0) / duration

    # send to client
    result_str = f"{throughput:.2f}"
    server_socket.sendto(result_str.encode("ascii"), client_address)

    # ssummary
    print("\nRESULT")
    print(f"Total bytes received: {total_bytes}")
    print(f"Time taken: {duration:.6f} seconds")
    print(f"Throughput: {result_str} KB/s")
else:
    print("[No data was received before timeout.")

server_socket.close()
print("Server closed.")
