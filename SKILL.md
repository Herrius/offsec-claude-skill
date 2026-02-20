---
name: offsec
description: Offensive security skill for pentesting, red team operations, network security, and CTF competitions. USE WHEN user needs help with reconnaissance, exploitation, security testing, offensive security tools, CTF strategy, or challenge prioritization.
---

# OffSec - Offensive Security Skill

Specialized skill for penetration testing, red team operations, network security assessments, and CTF competition strategy.

## Dynamic Context Loading (CRITICAL)

**This is NOT a passive reference.** As you work through any pentesting, red team, or CTF exercise, you MUST proactively consult the files in this skill directory based on what you DISCOVER during the workflow — not only when the user asks about a topic.

**Skill base path:** `/home/enrique/.claude/skills/offsec/`

### How It Works

Think of these files as your personal notes and cheatsheets. A real pentester checks their notes when they encounter something — you should do the same. **Read the relevant files at the moment you need them in your workflow**, not all upfront.

### Trigger: Discovery-Based Loading

Read the relevant files when YOUR OWN FINDINGS during the engagement trigger it:

| You discover / encounter... | Read these files |
|----------------------------|-----------------|
| Open ports, need to scan deeper | `tools/nmap.md` |
| A web application running | `workflows/web-pentest.md` + `tools/burp-suite.md` |
| Directories/vhosts to enumerate | `tools/ffuf-gobuster.md` |
| SQL injection vector | `tools/sqlmap.md` |
| Hashes to crack | `tools/hashcat-john.md` |
| Active Directory environment | `tools/bloodhound.md` + `tools/crackmapexec.md` + `tools/impacket.md` |
| ADCS / certificates in AD | `tools/certipy.md` |
| NTLM traffic, need to poison/relay | `tools/responder-relay.md` |
| Need to exploit with Metasploit | `configs/metasploit-commands.md` |
| PCAP to analyze | `configs/wireshark-filters.md` |
| Linux shell, need privesc | `tools/linpeas-winpeas.md` |
| Windows shell, need privesc | `tools/linpeas-winpeas.md` |
| Need a custom script/exploit | `scripts/` directory (read relevant script) |
| Need wordlists or web shells | `configs/custom-tools.md` |
| Starting a new engagement | `checklists/pre-engagement.md` + `workflows/combat-methodology.md` |
| Reconnaissance phase | `checklists/reconnaissance.md` |
| Writing the final report | `workflows/reporting.md` + `checklists/reporting.md` |
| Stuck or losing focus | `workflows/combat-methodology.md` |
| CTF competition | CTF Strategy section (this file, below) |

### Workflow Examples

**Example 1: Pentesting a box**
1. User says "pentest 10.10.10.5" → Read `checklists/reconnaissance.md` before starting nmap
2. Nmap finds port 80, 445 → Read `tools/nmap.md` for deeper enumeration flags, then `workflows/web-pentest.md` for the web app, and `tools/crackmapexec.md` for SMB
3. Web app has login form → Read `tools/burp-suite.md` + `tools/ffuf-gobuster.md`
4. Find SQLi → Read `tools/sqlmap.md`
5. Get credentials, dump hashes → Read `tools/hashcat-john.md`
6. Get shell, need privesc → Read `tools/linpeas-winpeas.md`

**Example 2: AD engagement**
1. User says "attack this AD lab" → Read `checklists/pre-engagement.md` + `workflows/network-pentest.md`
2. Find domain controller → Read `tools/crackmapexec.md` + `tools/bloodhound.md`
3. Responder catches hash → Read `tools/responder-relay.md` + `tools/hashcat-john.md`
4. Need Kerberos attack → Read `tools/impacket.md`
5. Find ADCS → Read `tools/certipy.md`

**Key rule: Read BEFORE you execute.** If you're about to run nmap, read `tools/nmap.md` first. If you found a hash, read `tools/hashcat-john.md` before cracking. This ensures you use optimal flags, techniques, and avoid common mistakes.

---

## When to Use This Skill

Invoke this skill when the user needs help with:
- Reconnaissance and information gathering
- Vulnerability assessment and exploitation
- Network security testing
- Pentesting methodologies and workflows
- Security tool usage (nmap, metasploit, wireshark, etc.)
- Custom exploit or tool development
- Post-exploitation techniques
- CTF competition strategy, challenge prioritization, and time management
- CTF scoring optimization (dynamic scoring, first blood)
- Post-competition analysis

## Critical Rule: Tool Installation Protocol

**BEFORE installing ANY tool, library, or dependency:**

1. **Check if an existing tool already does the same thing** — many offensive tools overlap in functionality. Don't install gobuster if ffuf is already available, don't install a Python library if a CLI tool already does the job.
2. **Verify the tool exists and is legitimate** — search for it, confirm it's a real project (GitHub, official docs), not a typo or non-existent package.
3. **Confirm it's needed for the specific task** — don't install "just in case". Only install if the current exercise or engagement requires it.
4. **Always use virtual environments** — Python: `venv` or `pipx`. Node: local `node_modules`. Never install globally unless absolutely necessary. This prevents dependency conflicts with the base system.
5. **Prefer tools already in the system** — check with `which <tool>`, `dpkg -l | grep <tool>`, or `pip list | grep <package>` before installing.

```bash
# Check if tool exists before installing
which nmap ffuf gobuster hashcat john 2>/dev/null

# Python: always use venv
python3 -m venv .venv && source .venv/bin/activate
pip install <package>

# Or use pipx for CLI tools (isolated by default)
pipx install <tool>
```

This applies to: Python libraries, system packages, standalone tools, and any dependency.

---

## Skill Contents

### Workflows (`workflows/`)
Detailed methodologies for common pentesting scenarios:
- **Combat methodology** — 7 domain-agnostic offensive mindset rules (bypass matrices, checklists, anti-tunnel-vision)
- **Reporting** — Pentesting deliverables, informe components, executive summary, findings, attack chains
- Web application pentesting
- Network penetration testing

### Tools (`tools/`)
Detailed usage guides for common offensive tools. Consult these when helping with specific tool usage:
- **nmap** — Port scanning, service enumeration, NSE scripts, evasion
- **ffuf & gobuster** — Web fuzzing, directory/subdomain discovery
- **hashcat & john** — Password cracking, hash identification, rules
- **bloodhound** — AD attack path analysis, collectors, Cypher queries
- **certipy** — ADCS exploitation (ESC1-ESC11), certificate abuse
- **crackmapexec (netexec)** — Network enumeration, lateral movement, credential spraying
- **burp suite** — Web app testing, proxy, intruder, repeater, extensions
- **impacket** — Remote execution, credential harvesting, Kerberos attacks, NTLM relay
- **sqlmap** — SQL injection automation, tamper scripts, OS shell
- **responder & ntlm relay** — Network poisoning, hash capture, relay attacks
- **linpeas & winpeas** — Privilege escalation enumeration (Linux/Windows)

### Scripts (`scripts/`)
Python templates and snippets for:
- Port scanners
- Exploit templates
- Enumeration scripts
- Post-exploitation tools

### Checklists (`checklists/`)
Step-by-step checklists for:
- Pre-engagement preparation
- Reconnaissance phase
- Exploitation phase
- Post-exploitation
- Reporting

### Configs (`configs/`)
Tool configurations and references:
- Metasploit commands (detailed reference)
- Wireshark filters (display/capture filters)
- Custom tool setups (Impacket, Scapy, wordlists, web shells)

## Quick Commands

**Reconnaissance:**
```bash
# Port scanning
nmap -sV -sC -p- -oA scan_results <target>

# Service enumeration
nmap -sV -p <ports> --script=banner,http-title,ssl-cert <target>

# DNS enumeration
dig any <domain> @<nameserver>
dnsrecon -d <domain>
```

**Network Testing:**
```bash
# Packet capture
tcpdump -i <interface> -w capture.pcap

# Network mapping
nmap -sn <network>/24
```

**Web Testing:**
```bash
# Directory bruteforce
ffuf -u http://<target>/FUZZ -w wordlist.txt

# Parameter fuzzing
wfuzz -c -z file,wordlist.txt http://<target>/?FUZZ=test
```

## Python Quick Snippets

**Basic TCP Scanner:**
```python
import socket
def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False
```

**HTTP Request with Requests:**
```python
import requests
response = requests.get('http://target',
                       headers={'User-Agent': 'Mozilla/5.0'},
                       timeout=5)
```

---

## CTF Competition Strategy

### The Competitive Formula

```
1st Place = Pre-preparation + Quick sweep of easy challenges +
            Strict time-boxing + First bloods +
            Hard challenges last + Zero rabbit holes
```

### Competition Phases

**Phase 0: Pre-Competition (days/weeks before)**
- Research the CTF: read writeups from previous editions to identify organizer style
- Pre-configure VM with all tools installed and tested
- Prepare scripts: auto-enumeration, crypto solvers, exploit templates
- Have cheatsheets ready: payloads, ROP templates, crypto references
- Essential bookmarks: CyberChef, dcode.fr, GTFOBins, HackTricks, PayloadsAllTheThings, RevShells

**Phase 1: Board Reconnaissance (first 30 minutes)**
- DO NOT start solving immediately
- Read ALL challenge titles, descriptions, and point values
- Classify each challenge: Sure (<15 min) / Probable / Unknown
- Identify first blood opportunities

**Phase 2: Quick Sweep (hours 1-3)**
- Solve ALL easy challenges first
- 15-minute rule: if no progress on an easy challenge, move on
- Goal: build solid point base and scoreboard presence

**Phase 3: Medium Challenges (hours 3-8)**
- Attack medium difficulty in your strong categories
- 30-minute rule: if no progress, rotate to another challenge
- Document everything attempted — solutions become obvious later

**Phase 4: Hard Challenges (hours 8+)**
- Now invest time in heavy challenges
- With dynamic scoring, one hard challenge can be worth more than 5 easy ones
- This phase defines first place

### CTF Category Quick-Reference

**Web:**
```
robots.txt → identify framework/version → dirbusting →
test SQLi/XSS/LFI/RCE on inputs → search known CVEs
```
Tools: Burp Suite, ffuf, gobuster, sqlmap, wfuzz

**Crypto:**
- Easy: Caesar, Base64, ROT13, XOR, Morse
- Medium: RSA with small values, Vigenère, weak hashes
- Hard: RSA factorization, elliptic curves, padding attacks
Tools: CyberChef, dcode.fr, RsaCtfTool, hashcat, john

**Forensics:**
```
file → strings → binwalk → exiftool
```
- PCAP: Wireshark → Follow TCP Stream → extract files
- Memory: Volatility → imageinfo → pslist → filescan
- Disk: Autopsy, FTK Imager, sleuthkit

**Steganography:**
```
exiftool → steghide → zsteg (PNG) → binwalk → spectrogram (audio)
```
Tools: steghide, zsteg, stegsolve, Audacity, binwalk

**Reverse Engineering:**
```
file → strings → ltrace/strace → Ghidra/IDA
```
- Static: Ghidra, IDA Free, radare2
- Dynamic: gdb + pwndbg/gef, ltrace, strace
- .NET/Java: dnSpy, JD-GUI, jadx

**PWN / Binary Exploitation:**
```
checksec → identify vuln → calculate offset → build exploit
```
| Protection | Bypass |
|-----------|--------|
| None | Direct shellcode |
| NX | ROP / ret2libc |
| Canary | Leak via format string |
| ASLR | Leak addresses, partial overwrite |
| PIE | Leak base address |
Tools: pwntools, ROPgadget, one_gadget

**OSINT / Misc:**
- Read description 3 times — hints are there
- Google dorking, Wayback Machine, file metadata
- Sometimes logic puzzles or scripting challenges

### Time Management

**24-48h CTFs:**
- Sleep at least 4-5 hours
- Before sleeping: leave long scripts running (brute force, fuzzing)
- Eat properly — low glucose = stupid mistakes
- 5 min break every 1.5h minimum

**6-8h CTFs:**
- No margin for rabbit holes. Brutal time-boxing
- If something doesn't work in allocated time, NEXT

**Golden Rule:** Never stay in a rabbit hole. If you feel you're forcing a solution, leave it and come back later.

**Most Common Mistake:** Spending 2 hours on a 100-point challenge while 5 challenges worth 50 points each sit untouched.

### Solo vs Team

**Solo:** Focus on strong categories first. Only touch weak ones after clearing strong. Automate everything.

**Team:** One person per category. One channel per category. Shared doc with real-time tracking. Rotate if stuck >30 min. Ideal roles: Web, Rev/PWN, Crypto, Forensics, OSINT/Misc/Scripting.

### Scoring Awareness

| Scoring Type | Strategy Implication |
|-------------|---------------------|
| Static | Point value is fixed — prioritize by difficulty/time ratio |
| Dynamic | Fewer solves = more points — hard challenges you CAN solve are gold |
| First Blood | Speed matters — if you know a category well, race for first solve |
| Decay | Points decrease over time — solve early for maximum value |

### Post-Competition Checklist

- Write writeups for everything solved (and attempted)
- Read writeups from teams that placed above you
- Add new tools/techniques to your arsenal
- Identify categories where you lost the most points
- Update scripts and cheatsheets with lessons learned

---

## Authorization Context

This skill assumes authorized security testing:
- Penetration testing engagements with written authorization
- CTF competitions and security challenges
- Personal lab environments and owned systems
- Security research and educational purposes

Always verify authorization before conducting security tests.

## Quick Reference

- **Tools:** See `tools/` directory for detailed tool usage guides
- **Workflows:** See `workflows/` directory for methodologies (combat mindset, web/network pentest, reporting)
- **Scripts:** See `scripts/` directory for Python templates
- **Checklists:** See `checklists/` directory for step-by-step guides
- **Configs:** See `configs/` directory for tool configurations

## Sources (CTF Strategy)

- [CTF Strategies & Techniques - Snyk](https://snyk.io/articles/ctf/strategies-techniques/)
- [CTF Field Guide - Trail of Bits](https://trailofbits.github.io/ctf/)
- [Strategies to Win a CTF - Cybrary](https://www.cybrary.it/blog/strategies-to-win-a-ctf-how-to-approach-a-jeopardy-style-ctf)
- [CTF Handbook - ctf101.org](https://ctf101.org/)

---

Generated: 2026-01-11 | CTF Strategy added: 2026-02-18 | Tools & Reporting added: 2026-02-19
