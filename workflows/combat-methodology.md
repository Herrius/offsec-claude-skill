# Combat Methodology — Offensive Mindset Rules

7 tactical rules for penetration testing, red team operations, and CTF competitions. These rules apply across **all offensive domains**: Linux, Windows, Active Directory, Web, Network, Binary/PWN, Crypto, Forensics, and OSINT.

---

## Rule 1: NEVER Discard a Vector for ONE Limitation

A blocked path is not a dead path. Every protection has bypass techniques. Before abandoning an attack vector, exhaust its bypass options.

### Bypass Matrix by Domain

**Linux Privilege Escalation:**

| Limitation | Bypass Techniques |
|-----------|-------------------|
| SUID not available | Check capabilities (`getcap -r /`), cron jobs, writable PATH dirs, LD_PRELOAD |
| sudo restricted | `sudo -l` for allowed commands → GTFOBins, env_keep abuse, sudoedit wildcard |
| Kernel hardened | Check loaded modules, container escapes, namespace abuse |
| SELinux/AppArmor | Find unconfined processes, check for permissive domains, profile bugs |
| No write to /tmp | Check /dev/shm, /var/tmp, user home, world-writable dirs |
| No compiler | Upload precompiled binary, use scripting languages (Python/Perl/Bash) |

**Windows / Active Directory:**

| Limitation | Bypass Techniques |
|-----------|-------------------|
| UAC enabled | fodhelper.exe, eventvwr.exe, computerdefaults.exe, DLL hijacking |
| AppLocker | Trusted paths (C:\Windows\Temp), LOLBAS, MSBuild, InstallUtil, Regsvr32 |
| AMSI active | Memory patching, obfuscation, reflection bypass, PowerShell downgrade (v2) |
| Constrained Language Mode | PowerShell v2 downgrade, C# via MSBuild, unmanaged code via Add-Type |
| Defender/AV | Living-off-the-land, custom loaders, process hollowing, syscall-based evasion |
| No admin → domain | Check for AS-REP roastable accounts, Kerberoastable SPNs, ADCS misconfigs |
| GPO restrictions | Check for writable GPO links, local policy vs domain policy conflicts |
| Credential Guard | Kerberos relay, shadow credentials, ADCS abuse (ESC1-ESC8) |

**Web Application:**

| Limitation | Bypass Techniques |
|-----------|-------------------|
| WAF blocking payloads | Encoding (URL, double, Unicode), case alternation, comment injection, HTTP smuggling |
| Input filters | Alternative syntax, polyglot payloads, different injection points (headers, cookies) |
| CSP blocking XSS | JSONP endpoints, CSP misconfiguration, base-uri abuse, trusted CDN injection |
| Auth bypass needed | Default creds, JWT manipulation, IDOR, parameter tampering, cookie forging |
| Rate limiting | IP rotation, header spoofing (X-Forwarded-For), distributed requests, timing gaps |
| File upload blocked | Extension tricks (.pHp, .php5, .phtml), content-type spoofing, double extensions, null byte |
| SSRF filters | Alternative IP formats (decimal, hex, octal), DNS rebinding, redirect chains |

**Network:**

| Limitation | Bypass Techniques |
|-----------|-------------------|
| Firewall blocking ports | Protocol tunneling (HTTP/DNS/ICMP), port forwarding, non-standard ports |
| IDS detecting exploits | Traffic fragmentation, encryption, timing manipulation, encoding payloads |
| Network segmentation | Pivot through compromised hosts, VLAN hopping, routing table manipulation |
| Egress filtering | DNS tunneling, HTTPS over allowed ports, ICMP tunneling |

**Binary / PWN:**

| Protection | Bypass Techniques |
|-----------|-------------------|
| NX (No Execute) | ROP chains, ret2libc, ret2csu, sigreturn-oriented programming (SROP) |
| Stack Canary | Format string leak, brute force (forking servers), info leak via other vuln |
| ASLR | Address leak, partial overwrite, ret2plt, brute force (32-bit) |
| PIE | Leak base address via format string or other info disclosure |
| Full RELRO | Target .bss, stack, or heap instead of GOT |
| Seccomp | Allowed syscall analysis, filter bypass via architecture confusion |

**Crypto:**

| Limitation | Bypass Techniques |
|-----------|-------------------|
| "Strong" encryption | Check implementation flaws, key reuse, IV reuse, ECB mode patterns |
| Unknown algorithm | Frequency analysis, known plaintext, crib dragging |
| Large key RSA | Check for shared factors (FactorDB), Wiener's attack (small e), Boneh-Durfee |
| Padding validation | Padding oracle attack, timing side channels |
| Hash "irreversible" | Rainbow tables, hashcat rules, known hash collisions |

**The principle:** Every security control was designed by a human. Humans make mistakes. Find the gap.

---

## Rule 2: Maximize CURRENT Position Before Pivoting

Extract everything possible from your current access level before seeking new footholds. Lateral movement introduces risk and noise.

### By Domain

**Linux foothold:**
- Enumerate everything as current user: files, processes, network, cron, history, env vars
- Check sudo permissions, SUID/capabilities, writable paths, mounted shares
- Read configs, credentials, SSH keys, bash_history, .env files
- Only after exhausting current user → pivot to another user

**Windows foothold:**
- whoami /all, net user, net localgroup administrators, cmdkey /list
- Check saved credentials, scheduled tasks, installed software, services
- Harvest browser passwords, WiFi profiles, registry secrets
- Enumerate from current context before seeking another user

**Web application:**
- LFI → chain to RCE (log poisoning, PHP wrappers, proc/self/environ)
- SSRF → map internal network, read cloud metadata, access internal services
- SQLi → extract all data → find credentials → access admin panel → upload shell
- XSS → steal sessions → escalate to admin → chain to further access
- Don't jump to the next vulnerability until the current one is fully milked

**Active Directory:**
- BloodHound from current user perspective first
- Check group memberships, ACLs, delegations, SPNs for current account
- AS-REP roast, Kerberoast from current context
- Enumerate shares, GPO, ADCS as current user
- Only then seek lateral movement to another account

**Network segment:**
- Full scan of accessible range before pivoting to next segment
- Enumerate all services, grab banners, check for default creds
- Harvest everything accessible from current position

**Binary exploitation:**
- Maximize info leaks before attempting final exploit
- Leak canary, then libc base, then stack address — chain systematically
- Don't rush to shell; build your primitive set first

**The principle:** Depth before breadth. The path to root/admin/shell is often through the current position, not a new one.

---

## Rule 3: Each Access Method Has a DIFFERENT Context

A shell from a web exploit is not the same as SSH. An IDOR is not the same as admin access. Always reassess your context after gaining new access.

### Context Differences

**Linux:**
- Reverse shell vs SSH vs cron job shell → different TTY, PATH, env vars, capabilities
- www-data vs user vs root → different file access, network capabilities, process visibility
- Container vs host → different filesystem, network namespace, kernel access

**Windows:**
- Local user vs domain user vs service account → different token privileges, group memberships
- Interactive vs non-interactive session → different credential access patterns
- High integrity vs medium integrity → UAC implications, registry access

**Web:**
- Anonymous vs authenticated → different endpoints, functionality, data access
- User role vs admin role → different business logic, configuration access
- Direct access vs through proxy/CDN → different headers, caching, IP context
- Frontend vs API → different validation, authentication mechanisms

**Active Directory:**
- Domain User vs Local Admin vs Domain Admin → vastly different attack surface
- Same forest vs cross-forest → different trust exploitation paths
- On-premises vs hybrid (Azure AD) → different persistence and escalation vectors

**Network:**
- Inside vs outside perimeter → different service exposure
- Same VLAN vs different segment → different access patterns
- VPN vs direct → different traffic visibility and routing

**The principle:** After every access transition, run your enumeration again. New context = new opportunities.

---

## Rule 4: Obligatory Checklist on Gaining New Access

Every time you gain a new foothold or escalate privileges, run the appropriate checklist. No exceptions. This is not optional — it's tactical discipline.

### Linux Foothold Checklist

```
□ id && whoami && hostname
□ uname -a && cat /etc/os-release
□ ip a && ss -tlnp && netstat -rn
□ ps aux --forest
□ sudo -l
□ find / -perm -4000 2>/dev/null (SUID)
□ getcap -r / 2>/dev/null (capabilities)
□ cat /etc/crontab && ls -la /etc/cron.*
□ ls -la /home/ && find /home -readable 2>/dev/null
□ cat ~/.bash_history ~/.mysql_history
□ find / -writable -type f 2>/dev/null | head -50
□ env && cat /proc/*/environ 2>/dev/null
□ mount && df -h && lsblk
□ cat /etc/passwd | grep -v nologin
□ find / -name "*.conf" -o -name "*.bak" -o -name "*.old" 2>/dev/null
□ Check for Docker/LXC: ls /.dockerenv, cat /proc/1/cgroup
```

### Windows Foothold Checklist

```
□ whoami /all
□ systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
□ net user && net localgroup administrators
□ ipconfig /all && netstat -ano
□ tasklist /svc
□ cmdkey /list (saved credentials)
□ reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
□ schtasks /query /fo LIST /v
□ wmic service list brief | findstr /i "auto"
□ dir /s /b C:\Users\*password* C:\Users\*.kdbx C:\Users\*.key 2>nul
□ Check PowerShell history: type %APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
□ Check installed software: wmic product get name,version
□ Check for AlwaysInstallElevated: reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
□ Check unquoted service paths: wmic service get name,pathname,displayname,startmode | findstr /i "auto"
```

### Web Application Access Checklist

```
□ Map all endpoints (sitemap, robots.txt, JS files, API docs)
□ Identify technology stack (Wappalyzer, headers, error pages)
□ Check for default credentials on admin panels
□ Test all input fields for injection (SQLi, XSS, SSTI, command injection)
□ Check for IDOR on every object reference
□ Review JavaScript for hardcoded secrets, API keys, hidden endpoints
□ Test file upload functionality (if exists)
□ Check for SSRF on any URL parameter
□ Review cookies and tokens (JWT decode, session predictability)
□ Check for directory traversal / LFI
□ Test authentication bypass (parameter tampering, forced browsing)
□ Check CORS and CSP configuration
```

### Active Directory Domain User Checklist

```
□ BloodHound collection (SharpHound or bloodhound-python)
□ whoami /all — check group memberships and privileges
□ net user /domain && net group "Domain Admins" /domain
□ Enumerate SPNs for Kerberoasting: GetUserSPNs.py
□ Check for AS-REP roastable accounts: GetNPUsers.py
□ Enumerate shares: smbclient -L //<DC> && CrackMapExec smb <range> --shares
□ Check for ADCS: certipy find -u user -p pass -dc-ip <DC>
□ Enumerate ACLs: Check for GenericAll, WriteDACL, WriteOwner on important objects
□ Check for delegation: Unconstrained, Constrained, RBCD
□ Enumerate GPOs for writable links or credentials in scripts
□ Check for LAPS: Get-LAPSPasswords or CrackMapExec
□ Test discovered credentials with spray: CrackMapExec smb <range> -u user -p pass
```

### Network Segment Access Checklist

```
□ Map the subnet: nmap -sn <range>
□ Full port scan on discovered hosts: nmap -sV -sC -p- <targets>
□ Check for default credentials on network devices
□ ARP scan for additional hosts: arp-scan -l
□ Check for SNMP: snmpwalk -v2c -c public <targets>
□ Test for LLMNR/NBT-NS poisoning opportunity
□ Check for null sessions: rpcclient -U "" <target>
□ Identify routing and additional subnets reachable from this position
□ Check for multicast protocols (mDNS, SSDP)
□ Capture traffic for credential harvesting opportunity
```

**The principle:** Discipline beats talent. Run the checklist every time, even when you think you already know what to look for.

---

## Rule 5: When Stuck > 1 Hour — Reset

If you've been stuck on the same vector for more than 1 hour without meaningful progress, you are in a rabbit hole. This rule is universal across all domains.

### The Reset Protocol

1. **STOP.** Step away from the keyboard for 5 minutes.
2. **Document** what you've tried and why it failed.
3. **Re-read** all your notes from the beginning. The answer is often in data you already collected.
4. **Ask yourself:**
   - Am I making assumptions I haven't verified?
   - Is there enumeration output I skimmed but didn't analyze?
   - Am I trying to force a specific attack path instead of following the evidence?
   - Did I miss a service, port, file, or endpoint?
5. **Reset your approach:**
   - Go back to enumeration with fresh eyes
   - Try a completely different attack category
   - Search for the specific technology + "exploit" or "vulnerability"
   - Read someone else's writeup for a similar scenario

### Common Rabbit Holes by Domain

| Domain | Typical Rabbit Hole | What to Do Instead |
|--------|--------------------|--------------------|
| Linux | Trying to exploit a kernel version for hours | Check simpler vectors: cron, SUID, sudo misconfig |
| Windows | Fighting AV evasion endlessly | Try living-off-the-land (LOLBAS) or different initial vector |
| Web | Manually crafting bypasses for one filter | Look for another input point or different vulnerability class |
| AD | Brute forcing one password | Enumerate more: SPNs, ADCS, ACLs, delegation |
| PWN | Trying one exploitation technique | Re-analyze the binary — maybe the vuln class is different |
| Crypto | Manual math on RSA | Try automated tools first (RsaCtfTool, FactorDB) |
| Network | Scanning the same range repeatedly | Check if you missed a VLAN, service, or protocol |

**The principle:** Time is your most valuable resource. Stubbornness is not a strategy.

---

## Rule 6: Investigation Hierarchy

When approaching any target, follow this priority order. It applies to every stage of an engagement.

```
1. EXPLOIT current position fully
   └─ Extract all value from where you ARE

2. SEEK horizontal movement
   └─ Same privilege level, different context (another user, another host, another app)

3. SEEK vertical escalation
   └─ Higher privilege level (user→admin, admin→root, local→domain)
```

### Applied Examples

**Web pentest:**
1. Exploit current vuln fully (SQLi → dump all DBs → find creds)
2. Horizontal: use found creds on other applications/panels
3. Vertical: admin panel → code execution → shell

**Linux privesc:**
1. Exploit current user fully (read all accessible files, check all permissions)
2. Horizontal: pivot to another user with found credentials/keys
3. Vertical: escalate to root via SUID/sudo/kernel

**Active Directory:**
1. Exploit current account fully (enumerate everything accessible)
2. Horizontal: move to another workstation/server with same creds
3. Vertical: escalate to Domain Admin via Kerberoasting/ACL abuse/ADCS

**Network pentest:**
1. Exploit current segment fully (all hosts, all services)
2. Horizontal: pivot to adjacent network segment
3. Vertical: gain access to management VLAN or domain controller

**The principle:** Most people jump to step 3 immediately. The path to victory usually goes 1 → 2 → 3 sequentially.

---

## Rule 7: Anti-Tunnel-Vision

You are not smarter than the system. If your "brilliant" attack isn't working, the problem is your assumption, not the target's defenses.

### Symptoms of Tunnel Vision

- You've been trying variations of the same payload for 30+ minutes
- You're convinced the vulnerability is X but can't prove it
- You're ignoring other services/ports/endpoints because "this one must be it"
- You're reading the same output repeatedly hoping to see something new
- You're googling the same thing with slightly different words

### The Antidote

1. **List every assumption you're making** — then question each one
2. **Read your enumeration output again**, line by line
3. **Look at what you HAVEN'T tried**, not what you have
4. **Ask: what if the vulnerability is in a completely different place?**
5. **Talk it out** — explain the problem aloud (rubber duck debugging)

### Domain-Specific Tunnel Vision Traps

**Web:** Fixating on SQLi when the real vuln is SSTI, or testing XSS when the business logic flaw is the actual path.

**Linux:** Obsessing over kernel exploits when there's a writable cron job or a misconfigured sudo entry.

**Windows:** Fighting to bypass AV when there's an unquoted service path or an AlwaysInstallElevated policy.

**AD:** Trying to crack hashes when there's a misconfigured ACL granting GenericAll on a Domain Admin.

**PWN:** Trying buffer overflow on a format string vulnerability, or building ROP when ret2libc is simpler.

**Crypto:** Implementing complex mathematical attacks when the key is reused or the IV is static.

**CTF:** Spending 2 hours on a 100-point challenge when five 50-point challenges sit unsolved.

**The principle:** The vulnerability is where it IS, not where you WANT it to be. Follow evidence, not ego.

---

## Summary

| # | Rule | Core Idea |
|---|------|-----------|
| 1 | Never discard for one limitation | Every protection has bypass techniques |
| 2 | Maximize current position | Depth before breadth |
| 3 | Each access = different context | Re-enumerate after every transition |
| 4 | Obligatory checklists | Discipline beats talent |
| 5 | Stuck > 1 hour = reset | Time is your most valuable resource |
| 6 | Investigation hierarchy | Exploit → Horizontal → Vertical |
| 7 | Anti-tunnel-vision | Follow evidence, not ego |

---

*These rules are domain-agnostic. They apply whether you're exploiting a web app, escalating privileges on Linux, attacking Active Directory, solving a CTF challenge, or conducting a full red team engagement. The mindset is the weapon — tools are just the delivery mechanism.*
