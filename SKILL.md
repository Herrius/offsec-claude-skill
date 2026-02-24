---
name: offsec
description: Offensive security skill for pentesting, red team operations, network security, CTFs, and security labs. USE WHEN user needs help with authorized pentesting engagements, red team exercises, exploitation, privilege escalation, Active Directory attacks, network security testing, CTF competitions, security tool usage, or writing pentest reports. This is for technical engagements with formal scope — NOT for bug bounty platform hunting (use bugbounty skill for that).
---

# OffSec - Offensive Security Skill

Pentesting, red team operations, network assessments, and CTF competitions.

## What I Can and Cannot Do

Understanding these boundaries prevents wasted time and bad advice:

- **I can:** Plan attack paths, generate tool commands with optimal flags, analyze scan output, suggest bypass techniques, explain exploitation chains, write pentest reports, help with post-exploitation strategy, generate custom exploit code, decode/crack hashes offline
- **I cannot:** Execute tools on targets directly, do real-time exploitation requiring precise timing (race conditions), analyze images reliably (steganography, OSINT visual, captchas), interact with live services iteratively, brute-force in real time
- **Use me for:** Strategy, command generation, output analysis, report writing, technique research
- **Don't rely on me for:** Live CTF solving in competition, timing-sensitive exploits, visual analysis

---

## Dynamic Context Loading

As you work through any engagement, proactively load the relevant files based on what you discover — not only when explicitly asked.

**Read BEFORE you execute.** If you're about to run nmap, read `tools/nmap.md` first. If you found a hash, read `tools/hashcat-john.md` before cracking.

### Trigger: Discovery-Based Loading

| You discover / encounter... | Read these files |
|----------------------------|-----------------|
| Open ports, need deeper scan | `tools/nmap.md` |
| Web application | `workflows/web-pentest.md` + `tools/burp-suite.md` |
| Directories/vhosts to enumerate | `tools/ffuf-gobuster.md` |
| SQL injection vector | `tools/sqlmap.md` |
| Hashes to crack | `tools/hashcat-john.md` |
| Active Directory environment | `tools/bloodhound.md` + `tools/crackmapexec.md` + `tools/impacket.md` |
| ADCS / certificates in AD | `tools/certipy.md` |
| NTLM traffic, need to poison/relay | `tools/responder-relay.md` |
| Metasploit exploitation | `configs/metasploit-commands.md` |
| PCAP to analyze | `configs/wireshark-filters.md` |
| Linux shell, need privesc | `tools/linpeas-winpeas.md` |
| Windows shell, need privesc | `tools/linpeas-winpeas.md` |
| Wordlists or web shells needed | `configs/custom-tools.md` |
| Starting a new engagement | `checklists/pre-engagement.md` + `workflows/combat-methodology.md` |
| Reconnaissance phase | `checklists/reconnaissance.md` |
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

### References (`references/`)
- **ctf-strategy.md** — CTF competition strategy, time management, category quick-reference
- **modern-attacks.md** — API security, HTTP smuggling, cache poisoning, cloud attacks

### Checklists (`checklists/`)
- Pre-engagement, reconnaissance, reporting

### Configs (`configs/`)
- Metasploit commands, Wireshark filters, custom tool setups

---

## Authorization Context

This skill assumes authorized security testing:
- Penetration testing engagements with written authorization
- CTF competitions and security challenges
- Personal lab environments and owned systems
- Security research and educational purposes
