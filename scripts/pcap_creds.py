#!/usr/bin/env python3
"""
PCAP Credential Extractor
Extracts cleartext credentials from PCAP files (FTP, HTTP Basic, Telnet, SMTP).
Requires: pyshark (pip install pyshark) or falls back to tshark CLI.

Usage: python3 pcap_creds.py <pcap_file> [--output results.txt]
"""

import subprocess
import sys
import json
from pathlib import Path


def extract_ftp(pcap_path: str) -> list[dict]:
    """Extract FTP USER/PASS pairs."""
    cmd = [
        "tshark", "-r", pcap_path,
        "-Y", "ftp.request.command == USER || ftp.request.command == PASS",
        "-T", "fields",
        "-e", "frame.number",
        "-e", "ftp.request.command",
        "-e", "ftp.request.arg",
        "-E", "separator=|"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    creds = []
    current_user = None
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        _, command, arg = parts[0], parts[1], parts[2]
        if command == "USER":
            current_user = arg
        elif command == "PASS" and current_user:
            creds.append({
                "protocol": "FTP",
                "username": current_user,
                "password": arg
            })
            current_user = None
    return creds


def extract_http_basic(pcap_path: str) -> list[dict]:
    """Extract HTTP Basic Auth credentials."""
    import base64
    cmd = [
        "tshark", "-r", pcap_path,
        "-Y", "http.authorization contains Basic",
        "-T", "fields",
        "-e", "http.host",
        "-e", "http.authorization",
        "-E", "separator=|"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    creds = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 2:
            continue
        host = parts[0]
        auth = parts[1].replace("Basic ", "")
        try:
            decoded = base64.b64decode(auth).decode()
            user, passwd = decoded.split(":", 1)
            creds.append({
                "protocol": "HTTP Basic",
                "host": host,
                "username": user,
                "password": passwd
            })
        except Exception:
            pass
    return creds


def extract_http_post(pcap_path: str) -> list[dict]:
    """Extract HTTP POST form data that looks like login forms."""
    cmd = [
        "tshark", "-r", pcap_path,
        "-Y", "http.request.method == POST",
        "-T", "fields",
        "-e", "http.host",
        "-e", "http.request.uri",
        "-e", "http.file_data",
        "-E", "separator=|"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    login_keywords = ["user", "login", "email", "pass", "pwd", "password", "passwd"]
    creds = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        host, uri, data = parts[0], parts[1], parts[2]
        if any(kw in data.lower() for kw in login_keywords):
            creds.append({
                "protocol": "HTTP POST",
                "host": host,
                "uri": uri,
                "form_data": data
            })
    return creds


def extract_telnet(pcap_path: str) -> list[dict]:
    """Extract Telnet session data (best effort)."""
    cmd = [
        "tshark", "-r", pcap_path,
        "-Y", "telnet.data",
        "-T", "fields",
        "-e", "telnet.data",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    if result.stdout.strip():
        return [{"protocol": "Telnet", "raw_data": result.stdout.strip()[:500]}]
    return []


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <pcap_file> [--output results.txt]")
        sys.exit(1)

    pcap_path = sys.argv[1]
    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    if not Path(pcap_path).exists():
        print(f"[-] File not found: {pcap_path}")
        sys.exit(1)

    # Check tshark
    check = subprocess.run(["which", "tshark"], capture_output=True)
    if check.returncode != 0:
        print("[-] tshark not found. Install wireshark-cli or tshark.")
        sys.exit(1)

    print(f"[*] Analyzing: {pcap_path}")
    print("-" * 50)

    all_creds = []

    # FTP
    ftp_creds = extract_ftp(pcap_path)
    all_creds.extend(ftp_creds)
    for c in ftp_creds:
        print(f"[+] FTP: {c['username']}:{c['password']}")

    # HTTP Basic
    http_basic = extract_http_basic(pcap_path)
    all_creds.extend(http_basic)
    for c in http_basic:
        print(f"[+] HTTP Basic ({c.get('host', '?')}): {c['username']}:{c['password']}")

    # HTTP POST
    http_post = extract_http_post(pcap_path)
    all_creds.extend(http_post)
    for c in http_post:
        print(f"[+] HTTP POST ({c.get('host', '?')}{c.get('uri', '?')}): {c['form_data'][:100]}")

    # Telnet
    telnet = extract_telnet(pcap_path)
    all_creds.extend(telnet)
    for c in telnet:
        print(f"[+] Telnet session data found (review manually)")

    print("-" * 50)
    print(f"[*] Total credentials found: {len(all_creds)}")

    if output_file and all_creds:
        with open(output_file, "w") as f:
            json.dump(all_creds, f, indent=2)
        print(f"[*] Results saved to: {output_file}")

    if not all_creds:
        print("[*] No cleartext credentials found. Try manual analysis with Wireshark.")


if __name__ == "__main__":
    main()
