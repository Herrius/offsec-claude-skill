# OffSec Skill — Claude Code

Offensive security skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Provides structured knowledge for penetration testing, red team operations, CTF competitions, and security tool usage.

## What is this?

A Claude Code skill that gives Claude deep context about offensive security workflows, tool usage, and methodology. When invoked, Claude references these files to provide accurate, practical guidance for authorized security testing.

## Structure

```
offsec/
├── SKILL.md                    # Main skill definition (auto-loaded)
├── workflows/
│   ├── combat-methodology.md   # 7 offensive mindset rules (domain-agnostic)
│   ├── reporting.md            # Pentesting deliverables & report components
│   ├── web-pentest.md          # Web application testing methodology
│   └── network-pentest.md      # Network penetration testing methodology
├── tools/
│   ├── nmap.md                 # Port scanning, NSE scripts, evasion
│   ├── ffuf-gobuster.md        # Web fuzzing & directory discovery
│   ├── hashcat-john.md         # Password cracking
│   ├── bloodhound.md           # AD attack path analysis
│   ├── certipy.md              # ADCS exploitation (ESC1-ESC11)
│   ├── crackmapexec.md         # Network enum & lateral movement
│   ├── burp-suite.md           # Web app security testing
│   ├── impacket.md             # Python network protocol toolkit
│   ├── sqlmap.md               # SQL injection automation
│   ├── responder-relay.md      # NTLM poisoning & relay attacks
│   └── linpeas-winpeas.md      # Privilege escalation enumeration
├── configs/
│   ├── metasploit-commands.md  # Metasploit quick reference
│   ├── wireshark-filters.md    # Display & capture filters
│   └── custom-tools.md         # Impacket, Scapy, wordlists, shells
├── checklists/
│   ├── pre-engagement.md       # Pre-engagement preparation
│   ├── reconnaissance.md       # Reconnaissance phase checklist
│   └── reporting.md            # Reporting checklist
└── scripts/
    ├── port_scanner.py         # TCP port scanner template
    ├── subdomain_enum.py       # Subdomain enumeration
    ├── reverse_shell.py        # Reverse shell template
    └── http_fuzzer.py          # HTTP fuzzer template
```

## Key Features

- **Combat Methodology** — 7 domain-agnostic offensive mindset rules covering bypass matrices, anti-tunnel-vision, investigation hierarchy, and obligatory checklists
- **Tool References** — Practical usage guides for 11+ common offensive tools with real-world patterns
- **CTF Strategy** — Competition phases, time management, scoring awareness, category quick-references
- **Reporting Guide** — Executive summary writing, attack chain documentation, finding structure, vocabulary for non-technical audiences
- **Installation Protocol** — Built-in rule to verify tools before installing, prefer existing tools, and always use virtual environments

## Usage

### With Claude Code

Place this directory in your Claude Code skills path:

```
~/.claude/skills/offsec/
```

The skill activates when you ask about offensive security topics. You can also invoke it directly with `/offsec`.

### Standalone Reference

Each markdown file works as a standalone reference guide. Browse `tools/` for quick-reference cheatsheets.

## Authorization Context

This skill assumes authorized security testing:
- Penetration testing engagements with written authorization
- CTF competitions and security challenges
- Personal lab environments and owned systems
- Security research and educational purposes

## License

MIT
