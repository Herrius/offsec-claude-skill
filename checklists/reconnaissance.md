# Reconnaissance

Two variants: a fast lab checklist (HTB, THM, CTFs) and a full engagement checklist (real pentests). The trigger table in SKILL.md tells you which to use.

---

## Lab Quick-Start (HTB / THM / CTFs)

For single-target boxes where you know the IP and the goal is flags. Get from "here's the IP" to "I know what to attack" in under 10 minutes.

### Step 1: Full port scan (2-3 minutes)

```bash
# All TCP ports, fast
nmap -Pn -sS -p- -T4 --min-rate 5000 <TARGET> -oA initial

# Parse open ports for deep scan
ports=$(grep -oP '\d+/open' initial.nmap | cut -d/ -f1 | tr '\n' ',' | sed 's/,$//')
nmap -sV -sC -p $ports <TARGET> -oA detailed
```

### Step 2: Quick decisions based on what's open

```
Port 80/443/8080? → Browse it manually. Check:
    - What is the app? (CMS, custom, API, dashboard)
    - Login page? Default creds first (admin:admin, admin:password)
    - Interesting URLs or parameters?
    - View source → comments, JS files, hidden paths
    - Check /robots.txt, /sitemap.xml
    Then: ffuf for directory enumeration

Port 21 (FTP)? → Try anonymous login:
    ftp <TARGET>  # user: anonymous, pass: (empty or email)

Port 445 (SMB)? → Enumerate shares:
    smbclient -L //<TARGET> -N
    crackmapexec smb <TARGET> --shares -u '' -p ''

Port 22 (SSH)? → Note version, save for later (need creds first)

Port 139/445 + 88 (Kerberos)? → Domain controller. Read tools/bloodhound.md

Other unusual ports? → Google "port XXXX exploit" or check with nmap scripts:
    nmap -sV --script=default,vuln -p <PORT> <TARGET>
```

### Step 3: Web app deep dive (if web service found)

```bash
# Directory enumeration
ffuf -u http://<TARGET>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -mc 200,301,302,403

# Virtual host enumeration (if hostname found)
ffuf -u http://<TARGET> -H "Host: FUZZ.<DOMAIN>" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <default_size>

# Tech stack identification
whatweb http://<TARGET>
curl -sI http://<TARGET>
```

### Step 4: Look for low-hanging fruit

Before going deep on any single vector, check all of these:
- **Default credentials** on every login form and service
- **IDOR** — if URLs have numeric IDs (`/data/1`, `/user/5`), enumerate a range to find other users' data
- **Source code** — view page source, check JS files for API endpoints or hardcoded secrets
- **Known CVEs** — search the exact service version: `searchsploit <service> <version>`
- **Config files** — try common paths: `.env`, `config.php`, `web.config`, `.git/HEAD`

### Step 5: Document as you go

```bash
# Create working directory
mkdir ~/target_name && cd ~/target_name

# Save all nmap output with -oA flag (already done in step 1)
# Log interesting findings immediately — you WILL forget otherwise
echo "Found IDOR at /data/0 — downloads PCAP" >> notes.txt
```

---

## Full Reconnaissance (Real Engagements)

For authorized pentests with defined scope, where thoroughness matters for the report.

### Passive Reconnaissance

Do this BEFORE sending a single packet to the target.

**Domain & Infrastructure:**
```bash
# WHOIS
whois target.com

# DNS records — all types
dig target.com ANY +noall +answer
dig target.com A AAAA MX NS TXT SOA

# Certificate transparency — discover subdomains
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# Subdomain enumeration
subfinder -d target.com -o subdomains.txt
amass enum -passive -d target.com -o amass_subdomains.txt

# ASN and IP ranges
whois -h whois.radb.net -- '-i origin AS<NUMBER>'

# Historical data
# Check Wayback Machine: web.archive.org
# Check SecurityTrails for DNS history
```

**OSINT:**
```bash
# Email harvesting
theHarvester -d target.com -b all

# Google dorks
# site:target.com filetype:pdf
# site:target.com inurl:admin
# site:target.com intitle:"index of"
# "target.com" password OR secret OR key

# GitHub search
# org:targetorg password OR secret OR key OR token
# "target.com" filename:.env

# Breach/credential databases
# Check haveibeenpwned API for known breaches
# Search dehashed.com (with authorization)
```

**Technology fingerprinting:**
```bash
# Identify CDN, WAF, hosting
dig target.com +short
curl -sI https://target.com | grep -i "server\|x-powered-by\|cf-ray\|x-amz"

# Shodan (passive)
shodan host <IP>
shodan search "hostname:target.com"
```

### Active Reconnaissance

**Network scanning:**
```bash
# Host discovery (for ranges)
nmap -sn <RANGE>/24 -oA host_discovery

# Port scanning — tiered approach
# Quick scan first
nmap -sS -T4 --min-rate 5000 -p- <TARGETS> -oA full_tcp
# Detailed service scan on open ports
nmap -sV -sC -p <OPEN_PORTS> <TARGETS> -oA service_detail
# UDP top 20 (don't skip)
nmap -sU --top-ports 20 <TARGETS> -oA udp_top20
```

**Web application recon:**
```bash
# Full tech stack
whatweb -a 3 https://target.com
nikto -h https://target.com

# Directory and file enumeration
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -mc 200,301,302,403 -o dirs.json
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt -mc 200,301,302,403 -o files.json

# Virtual host enumeration
ffuf -u https://target.com -H "Host: FUZZ.target.com" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <default_size>

# Crawl and extract endpoints
katana -u https://target.com -d 3 -o katana_endpoints.txt

# JS file analysis
# Download all JS, search for API routes, secrets, internal hostnames
```

**Service-specific enumeration:**
```bash
# SMB
crackmapexec smb <TARGET> --shares -u '' -p ''
enum4linux-ng <TARGET>

# SNMP
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt <TARGET>
snmpwalk -v2c -c public <TARGET>

# LDAP
ldapsearch -x -h <TARGET> -b "dc=target,dc=com"

# NFS
showmount -e <TARGET>
```

### Documentation Requirements

For real engagements, document EVERYTHING:

- [ ] All findings with timestamps
- [ ] Screenshots of each discovery
- [ ] Network diagram with discovered hosts
- [ ] Complete asset inventory (IPs, hostnames, services, versions)
- [ ] Attack surface map (entry points ranked by likelihood)
- [ ] Initial vulnerability hypotheses
- [ ] Tools used with exact commands

This documentation feeds directly into the report. See `workflows/reporting.md`.
