#!/usr/bin/env python3
"""
Simple TCP Port Scanner
Usage: python3 port_scanner.py <target> <start_port> <end_port>
"""

import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def scan_port(host, port, timeout=1):
    """
    Scan a single port on the target host.
    Returns (port, True) if open, (port, False) if closed.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            return (port, True, service)
        return (port, False, None)
    except socket.gaierror:
        print(f"Error: Hostname could not be resolved")
        return (port, False, None)
    except socket.error:
        print(f"Error: Could not connect to host")
        return (port, False, None)

def scan_range(host, start_port, end_port, threads=100):
    """
    Scan a range of ports using multiple threads.
    """
    print(f"[*] Starting scan on {host}")
    print(f"[*] Scanning ports {start_port}-{end_port}")
    print(f"[*] Started at {datetime.now()}")
    print("-" * 50)

    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(scan_port, host, port): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                print(f"[+] Port {port} is OPEN - {service}")
                open_ports.append((port, service))

    print("-" * 50)
    print(f"[*] Scan completed at {datetime.now()}")
    print(f"[*] Found {len(open_ports)} open ports")

    return open_ports

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <target> <start_port> <end_port>")
        print(f"Example: {sys.argv[0]} 192.168.1.1 1 1000")
        sys.exit(1)

    target = sys.argv[1]
    start_port = int(sys.argv[2])
    end_port = int(sys.argv[3])

    try:
        # Resolve hostname
        target_ip = socket.gethostbyname(target)
        print(f"[*] Resolved {target} to {target_ip}")
    except socket.gaierror:
        print(f"[-] Error: Could not resolve hostname {target}")
        sys.exit(1)

    # Scan ports
    open_ports = scan_range(target_ip, start_port, end_port)

    # Summary
    if open_ports:
        print("\n[*] Open ports summary:")
        for port, service in open_ports:
            print(f"    {port}/{service}")

if __name__ == "__main__":
    main()
