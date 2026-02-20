# Nmap — Network Mapper

Herramienta principal de descubrimiento de red y auditoría de seguridad. Escaneo de puertos, detección de servicios, fingerprinting de SO, y scripting NSE.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## Escaneos Fundamentales

### Descubrimiento de Hosts
```bash
# Ping sweep (sin escaneo de puertos)
nmap -sn 192.168.1.0/24

# Solo descubrimiento ARP (red local, más rápido y preciso)
nmap -PR -sn 192.168.1.0/24

# Sin ping (útil cuando ICMP está bloqueado)
nmap -Pn <target>

# Descubrimiento por TCP SYN a puertos específicos
nmap -PS22,80,443 -sn 192.168.1.0/24

# Descubrimiento por UDP
nmap -PU53,161 -sn 192.168.1.0/24
```

### Escaneo de Puertos
```bash
# Top 1000 puertos (default)
nmap <target>

# Todos los puertos TCP
nmap -p- <target>

# Puertos específicos
nmap -p 22,80,443,8080 <target>

# Rango de puertos
nmap -p 1-1000 <target>

# Top N puertos más comunes
nmap --top-ports 100 <target>

# Escaneo UDP (requiere root, más lento)
nmap -sU --top-ports 20 <target>

# TCP + UDP combinado
nmap -sS -sU -p T:80,443,U:53,161 <target>
```

### Detección de Servicios y SO
```bash
# Versión de servicios
nmap -sV <target>

# Versión + scripts default
nmap -sV -sC <target>

# Detección de SO
nmap -O <target>

# Agresivo (OS + versión + scripts + traceroute)
nmap -A <target>

# Intensidad de detección de versión (0-9, default 7)
nmap -sV --version-intensity 9 <target>
```

---

## Tipos de Escaneo

```bash
# SYN scan (default con root, más sigiloso)
nmap -sS <target>

# TCP connect (sin root, completa el handshake)
nmap -sT <target>

# ACK scan (detectar firewalls, no puertos abiertos)
nmap -sA <target>

# FIN scan (evasión de firewalls simples)
nmap -sF <target>

# Xmas scan
nmap -sX <target>

# NULL scan
nmap -sN <target>

# Window scan (detectar puertos filtrados)
nmap -sW <target>

# Idle/Zombie scan (completamente sigiloso)
nmap -sI <zombie_host> <target>
```

---

## Velocidad y Timing

```bash
# Templates de timing (T0=paranoico, T5=insano)
nmap -T0 <target>  # IDS evasion (muy lento)
nmap -T1 <target>  # Sneaky
nmap -T2 <target>  # Polite
nmap -T3 <target>  # Normal (default)
nmap -T4 <target>  # Aggressive (recomendado para labs/CTFs)
nmap -T5 <target>  # Insane (puede perder puertos)

# Control granular
nmap --min-rate 1000 <target>          # Mínimo 1000 paquetes/seg
nmap --max-retries 2 <target>          # Máximo 2 reintentos
nmap --host-timeout 5m <target>        # Timeout por host
nmap --scan-delay 1s <target>          # Delay entre probes
nmap --max-parallelism 10 <target>     # Máximo 10 probes paralelos
```

**Recomendación CTF/Lab:** `-T4 --min-rate 5000` para velocidad. En engagements reales, `-T2` o `-T3` para evitar detección.

---

## Nmap Scripting Engine (NSE)

### Categorías de Scripts
```bash
# Scripts por categoría
nmap --script=default <target>        # Scripts seguros y útiles (= -sC)
nmap --script=vuln <target>           # Detección de vulnerabilidades
nmap --script=safe <target>           # Scripts que no afectan el target
nmap --script=intrusive <target>      # Pueden afectar el target
nmap --script=discovery <target>      # Descubrimiento de información
nmap --script=auth <target>           # Autenticación
nmap --script=brute <target>          # Fuerza bruta
nmap --script=exploit <target>        # Explotación directa

# Múltiples categorías
nmap --script="vuln and safe" <target>
nmap --script="default or discovery" <target>

# Excluir categorías
nmap --script="not intrusive" <target>
```

### Scripts Esenciales por Servicio

**HTTP (80/443):**
```bash
nmap -p 80,443 --script=http-title,http-headers,http-methods <target>
nmap -p 80 --script=http-enum <target>              # Directorios comunes
nmap -p 80 --script=http-vuln* <target>              # Vulns HTTP
nmap -p 80 --script=http-shellshock --script-args uri=/cgi-bin/test.cgi <target>
nmap -p 80 --script=http-sql-injection <target>
nmap -p 80 --script=http-robots.txt <target>
nmap -p 443 --script=ssl-enum-ciphers <target>       # Ciphers SSL/TLS
nmap -p 443 --script=ssl-heartbleed <target>          # Heartbleed
nmap -p 80 --script=http-wordpress-enum <target>      # WordPress
```

**SMB (139/445):**
```bash
nmap -p 445 --script=smb-enum-shares,smb-enum-users <target>
nmap -p 445 --script=smb-vuln* <target>               # EternalBlue, etc.
nmap -p 445 --script=smb-os-discovery <target>
nmap -p 445 --script=smb-protocols <target>
nmap -p 445 --script=smb-brute <target>
```

**DNS (53):**
```bash
nmap -p 53 --script=dns-zone-transfer --script-args dns-zone-transfer.domain=target.com <target>
nmap -p 53 --script=dns-brute --script-args dns-brute.domain=target.com <target>
nmap -p 53 --script=dns-cache-snoop <target>
```

**SSH (22):**
```bash
nmap -p 22 --script=ssh-auth-methods <target>
nmap -p 22 --script=ssh-brute <target>
nmap -p 22 --script=ssh-hostkey <target>
nmap -p 22 --script=ssh2-enum-algos <target>
```

**SMTP (25):**
```bash
nmap -p 25 --script=smtp-enum-users <target>
nmap -p 25 --script=smtp-open-relay <target>
nmap -p 25 --script=smtp-vuln* <target>
```

**SNMP (161):**
```bash
nmap -sU -p 161 --script=snmp-info,snmp-brute,snmp-interfaces <target>
nmap -sU -p 161 --script=snmp-processes <target>
nmap -sU -p 161 --script=snmp-netstat <target>
```

**LDAP (389/636):**
```bash
nmap -p 389 --script=ldap-rootdse <target>
nmap -p 389 --script=ldap-search --script-args 'ldap.base="dc=domain,dc=com"' <target>
```

**MySQL (3306):**
```bash
nmap -p 3306 --script=mysql-info,mysql-enum <target>
nmap -p 3306 --script=mysql-brute <target>
nmap -p 3306 --script=mysql-databases --script-args mysqluser=root,mysqlpass=pass <target>
```

**MSSQL (1433):**
```bash
nmap -p 1433 --script=ms-sql-info <target>
nmap -p 1433 --script=ms-sql-brute <target>
nmap -p 1433 --script=ms-sql-xp-cmdshell --script-args mssql.username=sa,mssql.password=pass <target>
```

**RDP (3389):**
```bash
nmap -p 3389 --script=rdp-enum-encryption <target>
nmap -p 3389 --script=rdp-vuln-ms12-020 <target>    # BlueKeep check
```

**FTP (21):**
```bash
nmap -p 21 --script=ftp-anon <target>                # Anonymous login
nmap -p 21 --script=ftp-brute <target>
nmap -p 21 --script=ftp-vuln* <target>
```

---

## Output

```bash
# Todos los formatos a la vez
nmap -oA scan_results <target>    # Genera .nmap, .xml, .gnmap

# Formatos individuales
nmap -oN output.txt <target>      # Normal
nmap -oX output.xml <target>      # XML (importable a Metasploit)
nmap -oG output.gnmap <target>    # Grepable
nmap -oS output.txt <target>      # Script kiddie (broma, no usar)

# Verbose y debug
nmap -v <target>                  # Verbose
nmap -vv <target>                 # Más verbose
nmap -d <target>                  # Debug
```

---

## Evasión de Firewalls/IDS

```bash
# Fragmentación de paquetes
nmap -f <target>                  # Fragmentar a 8 bytes
nmap --mtu 16 <target>            # MTU personalizado

# Decoys (IPs señuelo)
nmap -D RND:5 <target>            # 5 decoys aleatorios
nmap -D 192.168.1.1,192.168.1.2,ME <target>  # Decoys específicos

# Source port spoofing
nmap --source-port 53 <target>    # Simular DNS
nmap --source-port 80 <target>    # Simular HTTP

# Timing lento
nmap -T0 --scan-delay 5s <target>

# Data length padding
nmap --data-length 50 <target>

# MAC address spoofing
nmap --spoof-mac 0 <target>       # MAC aleatorio
nmap --spoof-mac Dell <target>    # Vendor específico

# Badsum (test IDS — hosts reales descartan, IDS puede alertar)
nmap --badsum <target>
```

---

## Patrones de Uso Comunes

### Escaneo Inicial de CTF/Lab
```bash
# Paso 1: Quick scan
nmap -T4 --min-rate 5000 -p- <target> -oA initial

# Paso 2: Detallado en puertos abiertos
nmap -sV -sC -p <puertos_encontrados> <target> -oA detailed

# Paso 3: Vuln scan
nmap --script=vuln -p <puertos_encontrados> <target> -oA vulns
```

### Escaneo de Red Interna
```bash
# Descubrimiento
nmap -sn 10.10.10.0/24 -oA hosts

# Escaneo de hosts vivos
nmap -sV -sC -T4 -iL hosts_vivos.txt -oA network_scan

# Buscar vulnerabilidades conocidas
nmap --script=vuln -iL hosts_vivos.txt -oA vulns
```

### One-liner para Extraer Puertos
```bash
# Extraer puertos de gnmap para usar en escaneo detallado
grep -oP '\d+/open' initial.gnmap | cut -d/ -f1 | sort -un | tr '\n' ',' | sed 's/,$//'
```

---

## Tips

- **Siempre guardar output** con `-oA` — te ahorra re-escanear
- **UDP es lento** — solo escanear top 20-50 puertos UDP salvo que tengas razón para más
- **-sV puede ser ruidoso** — en engagements reales, considerar empezar sin él
- **Scripts NSE son poderosos** — `ls /usr/share/nmap/scripts/ | grep <servicio>` para ver disponibles
- **Importar a Metasploit** — `db_import scan.xml` en msfconsole para integrar resultados
