import socket
import os
import threading

SERVER_IP = "0.0.0.0"
SERVER_PORT = 69  # Sử dụng cổng không cần quyền admin
BUFFER_SIZE = 516
STORAGE_DIR = "server_storage"

def start_server():
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    def server_loop():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, SERVER_PORT))
        sock.settimeout(1.0)  # timeout để có thể kiểm tra việc dừng server
        print(f"[Server] Embedded TFTP server running on port {SERVER_PORT}...")

        while True:
            try:
                data, client_address = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                if not server_thread.is_alive():
                    break
                continue
            except OSError:
                break  # socket bị đóng

            opcode = int.from_bytes(data[:2], 'big')
            if opcode == 2:  # WRQ
                threading.Thread(target=handle_wrq, args=(data, client_address, sock)).start()

    def handle_wrq(data, client_address, server_socket):
        parts = data[2:].split(b'\x00')
        filename = parts[0].decode()
        file_path = os.path.join(STORAGE_DIR, filename)
        with open(file_path, 'wb') as f:
            ack_block_0 = b'\x00\x04\x00\x00'
            server_socket.sendto(ack_block_0, client_address)
            block_number = 1

            while True:
                try:
                    data_packet, _ = server_socket.recvfrom(BUFFER_SIZE)
                except socket.timeout:
                    break
                if data_packet[0:2] != b'\x00\x03':
                    continue
                recv_block = int.from_bytes(data_packet[2:4], 'big')
                data = data_packet[4:]
                if recv_block != block_number:
                    continue
                f.write(data)
                ack = b'\x00\x04' + recv_block.to_bytes(2, 'big')
                server_socket.sendto(ack, client_address)
                if len(data) < 512:
                    break
                block_number += 1

    # Tạo thread server
    global server_thread
    server_thread = threading.Thread(target=server_loop, daemon=True)
    server_thread.start()
