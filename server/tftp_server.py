import socket
import os
import threading
import time

SERVER_IP = "0.0.0.0"
SERVER_PORT = 69
BUFFER_SIZE = 516
STORAGE_DIR = "server_storage"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    filepath = os.path.join(STORAGE_DIR, filename)
    while os.path.exists(filepath):
        filename = f"{base}_{counter}{ext}"
        filepath = os.path.join(STORAGE_DIR, filename)
        counter += 1
    return filename, filepath

def handle_upload(client_address, filename):
    filename, filepath = get_unique_filename(filename)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.settimeout(5)
    data_socket.bind((SERVER_IP, 0))  # dùng port ngẫu nhiên
    server_port = data_socket.getsockname()[1]

    print(f"[+] Tạo session mới từ {client_address} - Port {server_port} - Lưu file {filename}")

    # Gửi ACK(0) từ socket mới
    ack = b'\x00\x04\x00\x00'
    data_socket.sendto(ack, client_address)

    expected_block = 1
    received_blocks = 0
    start_time = time.time()

    with open(filepath, 'wb') as f:
        while True:
            try:
                data, addr = data_socket.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                print("[!] Timeout - kết thúc kết nối.")
                break

            if len(data) < 4:
                continue

            opcode = data[1]
            if opcode != 3:  # không phải DATA
                continue

            block = int.from_bytes(data[2:4], "big")
            if block == expected_block:
                f.write(data[4:])
                received_blocks += 1
                expected_block += 1

            # Gửi ACK
            ack = b'\x00\x04' + data[2:4]
            data_socket.sendto(ack, client_address)

            if len(data[4:]) < 512:
                break

    data_socket.close()
    elapsed = time.time() - start_time
    size_kb = os.path.getsize(filepath) / 1024
    speed = size_kb / elapsed if elapsed > 0 else 0

    print(f"[✓] Nhận xong: {filename} ({size_kb:.2f} KB, {elapsed:.2f}s, {speed:.2f} KB/s)")

def main():
    print(f"[+] TFTP Server chạy trên cổng {SERVER_PORT}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if data[1] == 2:  # WRQ
            filename = data[2:].split(b'\x00')[0].decode(errors="ignore")
            threading.Thread(target=handle_upload, args=(addr, filename), daemon=True).start()

if __name__ == "__main__":
    main()
