import socket
import os
import time

BLOCK_SIZE = 512

def send_file(file_path, server_ip, port=69):  # 👈 Thêm port
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_data = f.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    # Gửi yêu cầu WRQ
    wrq_packet = b'\x00\x02' + file_name.encode() + b'\x00octet\x00'
    sock.sendto(wrq_packet, (server_ip, port))

    try:
        data, addr = sock.recvfrom(1024)
        if data[:2] != b'\x00\x04':
            return None
    except socket.timeout:
        return None

    total_blocks = (len(file_data) + BLOCK_SIZE - 1) // BLOCK_SIZE
    sent_blocks = 0
    acked_blocks = 0
    start_time = time.time()

    for block_num in range(1, total_blocks + 1):
        start = (block_num - 1) * BLOCK_SIZE
        end = start + BLOCK_SIZE
        data_block = file_data[start:end]

        data_packet = b'\x00\x03' + block_num.to_bytes(2, 'big') + data_block
        sock.sendto(data_packet, addr)
        sent_blocks += 1

        try:
            ack, _ = sock.recvfrom(1024)
            if ack[:2] == b'\x00\x04' and int.from_bytes(ack[2:4], 'big') == block_num:
                acked_blocks += 1
        except socket.timeout:
            continue  # Gói ACK bị mất, bỏ qua (mô phỏng mất gói)

    end_time = time.time()
    elapsed = end_time - start_time
    speed = len(file_data) / 1024 / elapsed if elapsed > 0 else 0
    loss = ((sent_blocks - acked_blocks) / sent_blocks) * 100 if sent_blocks else 0

    return {
        'sent_blocks': sent_blocks,
        'acked_blocks': acked_blocks,
        'packet_loss': loss,
        'transfer_speed': speed,
        'elapsed_time': elapsed
    }
