# Wireshark Filters Quick Reference

Common display and capture filters for network analysis.

---

## Display Filters Basics

```
# Protocol filters
tcp
udp
http
dns
icmp
arp

# Combine filters
tcp and port 80
http or dns
not arp
```

---

## IP Address Filters

```
# Source IP
ip.src == 192.168.1.100
ip.src == 192.168.1.0/24

# Destination IP
ip.dst == 10.10.10.50

# Either source or destination
ip.addr == 192.168.1.100

# Exclude IP
!(ip.addr == 192.168.1.1)

# IP range
ip.addr >= 192.168.1.1 and ip.addr <= 192.168.1.254
```

---

## Port Filters

```
# Specific port
tcp.port == 80
udp.port == 53

# Source port
tcp.srcport == 443

# Destination port
tcp.dstport == 22

# Port range
tcp.port >= 1000 and tcp.port <= 2000

# Common ports
tcp.port == 80 or tcp.port == 443 or tcp.port == 8080
```

---

## Protocol-Specific Filters

### HTTP/HTTPS
```
# HTTP traffic
http

# HTTP methods
http.request.method == "GET"
http.request.method == "POST"

# HTTP status codes
http.response.code == 200
http.response.code >= 400

# HTTP host
http.host == "example.com"

# HTTP URI
http.request.uri contains "admin"
http.request.uri contains "login"

# HTTP headers
http.user_agent contains "Mozilla"
http.cookie contains "session"

# HTTP errors
http.response.code >= 400

# POST data
http.request.method == "POST" and http.content_type contains "form"
```

### DNS
```
# All DNS
dns

# DNS queries
dns.flags.response == 0

# DNS responses
dns.flags.response == 1

# Specific query type
dns.qry.type == 1  # A record
dns.qry.type == 28 # AAAA record

# DNS query name
dns.qry.name contains "example.com"

# DNS errors
dns.flags.rcode != 0
```

### TCP
```
# TCP flags
tcp.flags.syn == 1
tcp.flags.ack == 1
tcp.flags.fin == 1
tcp.flags.rst == 1
tcp.flags.push == 1

# SYN packets only
tcp.flags.syn == 1 and tcp.flags.ack == 0

# TCP retransmissions
tcp.analysis.retransmission

# TCP connection issues
tcp.analysis.flags

# TCP stream
tcp.stream eq 0
```

### TLS/SSL
```
# TLS handshake
tls.handshake

# TLS client hello
tls.handshake.type == 1

# TLS server hello
tls.handshake.type == 2

# TLS certificate
tls.handshake.type == 11

# Server name (SNI)
tls.handshake.extensions_server_name contains "example.com"

# TLS version
tls.record.version == 0x0303  # TLS 1.2
```

### SMB
```
# SMB traffic
smb or smb2

# SMB commands
smb2.cmd == 5  # Create
smb2.cmd == 3  # Read
smb2.cmd == 9  # Write

# File names
smb2.filename contains "passwords"

# Authentication
ntlmssp
```

### FTP
```
# FTP commands
ftp

# FTP login
ftp.request.command == "USER"
ftp.request.command == "PASS"

# FTP file transfer
ftp-data
```

### SSH
```
# SSH traffic
ssh

# SSH version exchange
ssh.protocol contains "OpenSSH"
```

---

## Network Analysis Filters

### Broadcasts
```
# All broadcasts
eth.dst == ff:ff:ff:ff:ff:ff

# ARP broadcasts
arp

# DHCP broadcasts
bootp
```

### Suspicious Traffic
```
# Large packets
frame.len > 1500

# Many retransmissions (potential issues)
tcp.analysis.retransmission

# TCP resets
tcp.flags.reset == 1

# ICMP unreachable
icmp.type == 3

# Port scans (many SYN without ACK)
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

### Malicious Activity Indicators
```
# Potential C2 beaconing (regular intervals)
# Use IO Graph for this

# Base64 in HTTP (potential data exfiltration)
http contains "base64"

# Suspicious user agents
http.user_agent contains "python"
http.user_agent contains "curl"
http.user_agent contains "wget"

# Unusual DNS queries
dns.qry.name.len > 50

# Executable downloads
http.content_type contains "application/x-msdownload"
http.content_type contains "application/octet-stream"
```

---

## Advanced Filters

### Conversations
```
# Follow TCP stream
tcp.stream eq 0

# Follow UDP stream
udp.stream eq 0

# Follow HTTP stream
http.stream eq 0
```

### Time-based
```
# Specific time range
frame.time >= "2024-01-01 00:00:00" and frame.time <= "2024-01-01 01:00:00"

# Time delta
tcp.time_delta > 1
```

### Packet Length
```
# Small packets
frame.len < 60

# Large packets
frame.len > 1400

# Specific size
frame.len == 60
```

### Contains
```
# Contains string
tcp contains "password"
http contains "admin"
frame contains "malware"

# Case insensitive
tcp matches "(?i)password"
```

### Logical Operators
```
# AND
ip.src == 192.168.1.100 and tcp.port == 80

# OR
tcp.port == 80 or tcp.port == 443

# NOT
not arp

# Parentheses for grouping
(tcp.port == 80 or tcp.port == 443) and ip.src == 192.168.1.100
```

---

## Capture Filters (BPF Syntax)

**Note:** Capture filters use different syntax than display filters!

```
# Host
host 192.168.1.100

# Network
net 192.168.1.0/24

# Port
port 80
portrange 80-443

# Protocol
tcp
udp
icmp

# Combinations
tcp port 80
tcp dst port 443
src host 192.168.1.100 and dst port 22

# Not
not broadcast
not port 22
```

---

## Useful Filter Combinations

### Web Traffic Analysis
```
(http.request or tls.handshake.type == 1) and !(ssdp)
```

### Credential Hunting
```
http.request.method == "POST" or ftp.request.command == "PASS" or tcp contains "password"
```

### Malware Traffic
```
(http.request.uri contains ".exe" or http.request.uri contains ".dll") or (dns.qry.name matches ".*\\d{5,}.*")
```

### Network Issues
```
tcp.analysis.retransmission or tcp.analysis.duplicate_ack or tcp.analysis.lost_segment
```

### Data Exfiltration
```
(http.request.method == "POST" and http.content_length > 10000) or (dns.qry.name.len > 50)
```

---

## Coloring Rules

Useful coloring rules for quick analysis:

```
# Bad TCP (black background, red text)
tcp.analysis.flags and not tcp.analysis.window_update

# HTTP GET (green background)
http.request.method == "GET"

# HTTP POST (yellow background)
http.request.method == "POST"

# DNS (blue background)
dns

# Broadcast (yellow background)
eth.dst == ff:ff:ff:ff:ff:ff
```

---

## Statistics & Analysis

**Useful menu items:**

1. **Statistics → Conversations**
   - Shows all conversations between hosts
   - Useful for identifying top talkers

2. **Statistics → Protocol Hierarchy**
   - Shows protocol distribution
   - Good for overview of traffic types

3. **Statistics → IO Graphs**
   - Visual representation of traffic over time
   - Great for detecting beaconing

4. **Statistics → Endpoints**
   - Shows all endpoints in capture
   - Traffic volume per host

5. **Analyze → Follow → TCP Stream**
   - Reconstructs full conversation
   - Essential for analyzing application data

6. **Analyze → Expert Information**
   - Shows warnings and errors
   - Quick way to find issues

---

## Export Objects

Extract files from packet captures:

1. **File → Export Objects → HTTP**
   - Extract files downloaded via HTTP

2. **File → Export Objects → SMB**
   - Extract files transferred via SMB

3. **File → Export Objects → FTP-DATA**
   - Extract files transferred via FTP

---

## Tips & Tricks

```
# Quick bookmarks
Ctrl+M - Mark packet
Ctrl+Shift+M - Unmark all
Ctrl+N - Next marked
Ctrl+B - Previous marked

# Display filter history
Recent display filters are saved
Use up/down arrows in filter bar

# Clear display filter
Ctrl+/

# Apply as filter
Right-click packet → Apply as Filter

# Colorize conversation
Right-click packet → Colorize Conversation

# Time display format
View → Time Display Format
```

---

## Common Analysis Workflows

### 1. Initial Triage
```
1. Check Protocol Hierarchy
2. Look at Conversations
3. Check Expert Information
4. Apply relevant filters
```

### 2. Web Traffic Analysis
```
1. Filter: http or tls
2. Export HTTP objects
3. Check for suspicious URIs
4. Analyze POST requests
```

### 3. Malware Analysis
```
1. Filter DNS for unusual patterns
2. Check for HTTP downloads
3. Look for beaconing in IO Graph
4. Extract suspicious files
```

### 4. Network Troubleshooting
```
1. Filter for TCP analysis flags
2. Check for retransmissions
3. Look at time deltas
4. Analyze specific streams
```

---

## Security Notes

- Captures may contain sensitive data (passwords, cookies, etc.)
- Store captures securely
- Redact sensitive information before sharing
- Follow data handling procedures
- Respect privacy and legal requirements
