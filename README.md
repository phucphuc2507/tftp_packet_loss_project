# TFTP Packet Loss Analyzer and Transfer Tool

## Overview
This project simulates a TFTP-based file transfer system developed in Python, with added capabilities to measure and analyze packet loss, speed, and time during data transmission. It does not rely on any third-party TFTP libraries, making it suitable for educational and low-level protocol study.

## Key Components
- **Custom TFTP Server**  
  Listens on UDP port 69, receives/sends files via WRQ and RRQ operations. Supports file renaming to avoid overwriting existing data.

- **Client Core Logic**  
  Handles block-based file sending/receiving with ACKs. Calculates transfer metrics like lost packets, elapsed time, and speed.

- **Graphical User Interface (GUI)**  
  Built using `tkinter`, the GUI allows users to select files, input server IP, and view real-time progress and statistics.

- **Auto Server Startup**  
  The server is automatically launched as a background process when the GUI opens.

## Technical Features
- UDP socket communication using raw `socket` module
- Fully supports TFTP upload (WRQ) and download (RRQ)
- Packet loss detection by comparing blocks sent vs ACKed
- File size-aware speed calculation
- Cross-platform compatible (tested on Windows)
- Clean separation between client GUI, core logic, and server

## Use Cases
- Teaching how TFTP and UDP transmission works
- Simulating packet loss in real-world environments
- Networking tool for measuring file transfer reliability

## Requirements
- Python 3.10+
- `psutil` for server process detection
- `tkinter` for GUI (built-in on most Python installs)
