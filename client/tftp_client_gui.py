import tkinter as tk
from tkinter import filedialog, messagebox
import os
import tftp_client_core
from core import tftp_server_embedded

# 🔹 Khởi động server ngầm ngay khi GUI khởi chạy
tftp_server_embedded.start_server()


def browse_file():
    filename = filedialog.askopenfilename()
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

def start_transfer():
    filename = file_entry.get()
    server_ip = ip_entry.get()

    if not filename or not os.path.exists(filename):
        messagebox.showerror("Lỗi", "Vui lòng chọn file hợp lệ.")
        return

    if not server_ip:
        messagebox.showerror("Lỗi", "Vui lòng nhập IP của TFTP Server.")
        return

    result_label.config(text="Đang upload...")
    root.update()

    try:
        stats = tftp_client_core.send_file(filename, server_ip, port=69)  # dùng đúng port đã đổi

        if stats is None:
            result_label.config(text="❌ Upload thất bại. Không nhận được phản hồi từ server.")
            return

        result_label.config(
            text=f"""✅ Upload hoàn tất!
Blocks đã gửi: {stats['sent_blocks']}
ACK nhận: {stats['acked_blocks']}
Mất gói: {stats['packet_loss']:.2f}%
Tốc độ: {stats['transfer_speed']:.2f} KB/s
Thời gian: {stats['elapsed_time']:.2f} giây"""
        )

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("TFTP Packet Loss Client")
root.geometry("500x350")
root.resizable(False, False)

tk.Label(root, text="Chọn file:").pack(pady=5)
file_frame = tk.Frame(root)
file_frame.pack()
file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side=tk.LEFT, padx=5)
tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT)

tk.Label(root, text="Nhập IP Server:").pack(pady=5)
ip_entry = tk.Entry(root, width=30)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack()

tk.Button(root, text="Upload", command=start_transfer, bg="#007bff", fg="white", width=20).pack(pady=15)

result_label = tk.Label(root, text="", justify=tk.LEFT, font=("Arial", 10))
result_label.pack(pady=10)

root.mainloop()
