import socket
import os
import sys  # Missing import added

# Create a raw socket
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

# Bind to all interfaces (to avoid specific IP binding issues)
sniffer.bind(("0.0.0.0", 0))

# Set socket option to include IP headers
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# Enable promiscuous mode on Windows
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

print("Sniffing packets... Press Ctrl+C to stop.")

try:
    while True:
        packet_data, addr = sniffer.recvfrom(65565)
        print(f"Packet from {addr}: {packet_data}")
except KeyboardInterrupt:
    print("\nStopping packet sniffing...")

    # Disable promiscuous mode on Windows
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    sniffer.close()
    sys.exit(0)
