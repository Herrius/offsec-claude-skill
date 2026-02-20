# Reconnaissance Checklist

Comprehensive information gathering phase checklist.

---

## Passive Reconnaissance

### OSINT - Open Source Intelligence

**Domain Information:**
- [ ] WHOIS lookup performed
- [ ] DNS records enumerated (A, AAAA, MX, NS, TXT, SOA)
- [ ] Historical DNS data checked
- [ ] Domain registration info gathered
- [ ] Registrar information documented
- [ ] Domain age identified
- [ ] SSL/TLS certificate information extracted

**Subdomain Discovery:**
- [ ] Certificate transparency logs checked
- [ ] Search engine dorking performed
- [ ] DNS brute forcing completed
- [ ] Zone transfer attempted
- [ ] Subdomain takeover possibilities identified

**Organization Information:**
- [ ] Company structure researched
- [ ] Key personnel identified
- [ ] Email formats discovered
- [ ] Phone numbers collected
- [ ] Physical locations identified
- [ ] Social media profiles found

**Technical Footprint:**
- [ ] ASN and IP ranges identified
- [ ] Hosting provider determined
- [ ] CDN usage identified
- [ ] Technology stack identified
- [ ] Third-party services documented
- [ ] API endpoints discovered

**Data Leaks:**
- [ ] Breach databases checked
- [ ] Pastebin searches performed
- [ ] GitHub/GitLab repositories searched
- [ ] Credentials in public repos checked
- [ ] Exposed documents found
- [ ] Metadata from documents analyzed

---

## Active Reconnaissance

### Network Enumeration

**Host Discovery:**
- [ ] Ping sweeps performed
- [ ] ARP scans completed (if local)
- [ ] Live hosts identified
- [ ] Network ranges mapped

**Port Scanning:**
- [ ] Quick scan (top 1000 ports)
- [ ] Full port scan (1-65535)
- [ ] UDP scan performed
- [ ] Service version detection
- [ ] OS fingerprinting completed

**Service Enumeration:**
- [ ] Banner grabbing performed
- [ ] Service-specific enumeration:
  - [ ] HTTP/HTTPS (web servers)
  - [ ] FTP (file transfer)
  - [ ] SSH (remote access)
  - [ ] Telnet
  - [ ] SMTP (email)
  - [ ] DNS (domain name)
  - [ ] SMB/NetBIOS (file sharing)
  - [ ] SNMP (network management)
  - [ ] LDAP (directory services)
  - [ ] RDP (remote desktop)
  - [ ] Database services

---

## Web Application Recon

**Technology Identification:**
- [ ] Web server identified
- [ ] Application framework detected
- [ ] Programming language identified
- [ ] CMS identified (if applicable)
- [ ] JavaScript libraries identified
- [ ] WAF/security controls detected

**Content Discovery:**
- [ ] Directory enumeration completed
- [ ] File enumeration performed
- [ ] Hidden parameters discovered
- [ ] Backup files searched
- [ ] Source code comments reviewed
- [ ] Robots.txt examined
- [ ] Sitemap.xml retrieved

**Application Mapping:**
- [ ] Site spidered/crawled
- [ ] All endpoints documented
- [ ] Input vectors identified
- [ ] Authentication mechanisms mapped
- [ ] Session management reviewed
- [ ] API endpoints discovered

---

## Social Engineering Recon

**Personnel:**
- [ ] Employee names collected
- [ ] Email addresses harvested
- [ ] Job roles identified
- [ ] Organization chart mapped
- [ ] Key decision makers identified

**Social Media:**
- [ ] LinkedIn profiles reviewed
- [ ] Twitter accounts found
- [ ] Facebook presence checked
- [ ] Professional blogs identified
- [ ] Conference presentations found

**Physical Security:**
- [ ] Office locations identified
- [ ] Building access methods noted
- [ ] Security measures observed
- [ ] Employee routines identified (if authorized)

---

## Wireless Reconnaissance (if in scope)

- [ ] Wireless networks identified
- [ ] SSIDs collected
- [ ] Encryption methods noted
- [ ] Signal strength measured
- [ ] Access point locations mapped
- [ ] Hidden networks detected

---

## Cloud Infrastructure

**AWS:**
- [ ] S3 buckets enumerated
- [ ] Public snapshots checked
- [ ] EC2 instances identified
- [ ] Lambda functions discovered

**Azure:**
- [ ] Storage accounts enumerated
- [ ] Public blobs identified
- [ ] VM instances located

**GCP:**
- [ ] Storage buckets found
- [ ] Compute instances identified

---

## Documentation

- [ ] All findings documented
- [ ] Screenshots collected
- [ ] Network diagrams created
- [ ] Asset inventory compiled
- [ ] Attack surface mapped
- [ ] Initial vulnerabilities noted

---

## Tools Used

Document which tools were used:
- [ ] nmap
- [ ] subfinder/sublist3r
- [ ] amass
- [ ] whatweb
- [ ] nikto
- [ ] gobuster/ffuf
- [ ] recon-ng
- [ ] theHarvester
- [ ] shodan
- [ ] Custom scripts

---

## Next Steps

- [ ] Prioritize targets for exploitation
- [ ] Identify high-value targets
- [ ] Plan vulnerability assessment phase
- [ ] Brief team on findings
- [ ] Update client on progress

---

## Notes

```
Key findings and observations:

[Space for engagement-specific notes]
```
