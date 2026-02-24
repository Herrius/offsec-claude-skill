---
name: offsec
description: Offensive security skill for pentesting, red team operations, network security, CTFs, and security labs. USE WHEN user needs help with authorized pentesting engagements, red team exercises, exploitation, privilege escalation, Active Directory attacks, network security testing, CTF competitions, security tool usage, or writing pentest reports. This is for technical engagements with formal scope — NOT for bug bounty platform hunting (use bugbounty skill for that).
---

# OffSec - Offensive Security Skill

Pentesting, red team operations, network assessments, and CTF competitions.

## What I Can and Cannot Do

Understanding these boundaries prevents wasted time and bad advice:

- **I can:** Plan attack paths, generate tool commands with optimal flags, analyze scan output, suggest bypass techniques, explain exploitation chains, write pentest reports, help with post-exploitation strategy, generate custom exploit code, decode/crack hashes offline
- **I cannot:** Execute tools on targets directly, do real-time exploitation requiring precise timing (race conditions), analyze images reliably (steganography, OSINT visual, captchas), interact with live services iteratively, brute-force in real time, operate GUI tools (RDP, Burp UI, browser)
- **Use me for:** Strategy, command generation, output analysis, report writing, technique research
- **Don't rely on me for:** Live CTF solving in competition, timing-sensitive exploits, visual analysis

### Nested SSH and Special Characters in Passwords

When operating through a jump box (e.g., SSH to Kali VM, then SSH to target), passwords with special characters (`!`, `$`, backticks, etc.) break due to bash expansion across multiple shell layers. Inline `sshpass -p 'P@ss!word'` will fail silently or mangle the password.

**Fix:** Write a helper script on the jump box that uses `SSHPASS` env variable:

```bash
# Create on the jump box (e.g., ~/connect.sh)
cat > ~/connect.sh << 'SCRIPT'
#!/bin/bash
export SSHPASS="Buck3tH4TF0RM3!"
sshpass -e ssh -o StrictHostKeyChecking=no user@TARGET "$@"
SCRIPT
chmod +x ~/connect.sh

# Then use it for all commands on the target
~/connect.sh 'id && cat /home/user/user.txt'
~/connect.sh 'getcap -r / 2>/dev/null'
```

The `<< 'SCRIPT'` (quoted heredoc) prevents any expansion, and `sshpass -e` reads from the environment instead of the command line. Always use this pattern when passwords contain shell-special characters.

---

## Dynamic Context Loading

As you work through any engagement, proactively load the relevant files based on what you discover — not only when explicitly asked.

**Read BEFORE you execute.** If you're about to run nmap, read `tools/nmap.md` first. If you found a hash, read `tools/hashcat-john.md` before cracking.

### Trigger: Discovery-Based Loading

| You discover / encounter... | Read these files |
|----------------------------|-----------------|
| Open ports, need deeper scan | `tools/nmap.md` |
| Web application | `workflows/web-pentest.md` + `tools/burp-suite.md` |
| Incremental IDs in URLs (IDOR) | `workflows/web-pentest.md` (IDOR section) |
| Directories/vhosts to enumerate | `tools/ffuf-gobuster.md` |
| SQL injection vector | `tools/sqlmap.md` |
| Hashes to crack | `tools/hashcat-john.md` |
| Credentials found (any source) | `references/credential-reuse.md` |
| PCAP file to analyze | `configs/wireshark-filters.md` + `scripts/pcap_creds.py` |
| Active Directory environment | `tools/bloodhound.md` + `tools/crackmapexec.md` + `tools/impacket.md` |
| ADCS / certificates in AD | `tools/certipy.md` |
| NTLM traffic, need to poison/relay | `tools/responder-relay.md` |
| UDP 500/4500 (IKE/IPsec VPN) | `tools/ike-vpn.md` |
| Metasploit exploitation | `configs/metasploit-commands.md` |
| Linux shell, need privesc | `tools/linpeas-winpeas.md` + check `getcap -r / 2>/dev/null` |
| Windows shell, need privesc | `tools/linpeas-winpeas.md` |
| Wordlists or web shells needed | `configs/custom-tools.md` |
| Starting a new engagement | `checklists/pre-engagement.md` + `workflows/combat-methodology.md` |
| Reconnaissance phase (HTB/CTF/lab) | `checklists/reconnaissance.md` (Lab Quick-Start section) |
| Reconnaissance phase (real engagement) | `checklists/reconnaissance.md` (Full section) |
| Machine completed (flags obtained) | Generate formal writeup using Obsidian template `99 - Sistema/📋 plantillas/Plantilla - Writeup CTF.md` → save to `199 - maquinas/<machine_name>.md` |
| Writing the final report | `workflows/reporting.md` + `checklists/reporting.md` |
| Stuck or losing focus | `workflows/combat-methodology.md` |
| CTF competition | `references/ctf-strategy.md` |
| API / modern web attacks | `references/modern-attacks.md` |

### Workflow Examples

**Pentesting a box:**
1. "pentest 10.10.10.5" → Read `checklists/reconnaissance.md` before nmap
2. Nmap finds port 80, 445 → Read `tools/nmap.md`, `workflows/web-pentest.md`, `tools/crackmapexec.md`
3. Web app has login → Read `tools/burp-suite.md` + `tools/ffuf-gobuster.md`
4. Find SQLi → Read `tools/sqlmap.md`
5. Dump hashes → Read `tools/hashcat-john.md`
6. Get shell → Read `tools/linpeas-winpeas.md`

**AD engagement:**
1. "attack this AD lab" → Read `checklists/pre-engagement.md` + `workflows/network-pentest.md`
2. Find DC → Read `tools/crackmapexec.md` + `tools/bloodhound.md`
3. Responder catches hash → Read `tools/responder-relay.md` + `tools/hashcat-john.md`
4. Kerberos attack → Read `tools/impacket.md`
5. Find ADCS → Read `tools/certipy.md`

---

## Tool Installation Protocol

Before installing ANY tool:

1. **Check if an existing tool already does it** — don't install gobuster if ffuf is available
2. **Verify it exists and is legitimate** — confirm on GitHub/official docs
3. **Confirm it's needed** — don't install "just in case"
4. **Use virtual environments** — Python: `venv`/`pipx`. Node: local `node_modules`. Never global
5. **Prefer system tools** — check with `which <tool>` first

---

## Skill Contents

### Workflows (`workflows/`)
- **combat-methodology.md** — 7 offensive mindset rules (bypass matrices, checklists, anti-tunnel-vision)
- **reporting.md** — Pentest deliverables: executive summary, attack chains, findings, appendices
- **web-pentest.md** — Web app assessment decision trees and attack patterns
- **network-pentest.md** — Network/infrastructure pentest methodology

### Tools (`tools/`)
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
- **ike-vpn** — IKE/IPsec VPN enumeration, PSK cracking, VPN connection (ike-scan, psk-crack, vpnc, strongswan)

### References (`references/`)
- **ctf-strategy.md** — CTF competition strategy, time management, category quick-reference
- **modern-attacks.md** — API security, HTTP smuggling, cache poisoning, cloud attacks
- **credential-reuse.md** — What to do when you find credentials: where to spray, reuse patterns

### Scripts (`scripts/`)
- **pcap_creds.py** — Extract credentials from PCAP files (FTP, HTTP Basic, Telnet)

### Checklists (`checklists/`)
- Pre-engagement, reconnaissance (with lab quick-start variant), reporting

### Configs (`configs/`)
- Metasploit commands, Wireshark filters, custom tool setups

---

## Authorization Context

This skill assumes authorized security testing:
- Penetration testing engagements with written authorization
- CTF competitions and security challenges
- Personal lab environments and owned systems
- Security research and educational purposes
