# CTF Competition Strategy

## The Competitive Formula

```
1st Place = Pre-preparation + Quick sweep of easy challenges +
            Strict time-boxing + First bloods +
            Hard challenges last + Zero rabbit holes
```

## Competition Phases

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

## Category Quick-Reference

**Web:**
```
robots.txt → identify framework/version → dirbusting →
test SQLi/XSS/LFI/RCE on inputs → search known CVEs
```
Tools: Burp Suite, ffuf, gobuster, sqlmap, wfuzz

**Crypto:**
- Easy: Caesar, Base64, ROT13, XOR, Morse
- Medium: RSA with small values, Vigenere, weak hashes
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

## Time Management

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

## Solo vs Team

**Solo:** Focus on strong categories first. Only touch weak ones after clearing strong. Automate everything.

**Team:** One person per category. One channel per category. Shared doc with real-time tracking. Rotate if stuck >30 min. Ideal roles: Web, Rev/PWN, Crypto, Forensics, OSINT/Misc/Scripting.

## Scoring Awareness

| Scoring Type | Strategy Implication |
|-------------|---------------------|
| Static | Point value is fixed — prioritize by difficulty/time ratio |
| Dynamic | Fewer solves = more points — hard challenges you CAN solve are gold |
| First Blood | Speed matters — if you know a category well, race for first solve |
| Decay | Points decrease over time — solve early for maximum value |

## Post-Competition Checklist

- Write writeups for everything solved (and attempted)
- Read writeups from teams that placed above you
- Add new tools/techniques to your arsenal
- Identify categories where you lost the most points
- Update scripts and cheatsheets with lessons learned

---

## Sources

- [CTF Strategies & Techniques - Snyk](https://snyk.io/articles/ctf/strategies-techniques/)
- [CTF Field Guide - Trail of Bits](https://trailofbits.github.io/ctf/)
- [Strategies to Win a CTF - Cybrary](https://www.cybrary.it/blog/strategies-to-win-a-ctf-how-to-approach-a-jeopardy-style-ctf)
- [CTF Handbook - ctf101.org](https://ctf101.org/)
