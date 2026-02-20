# ffuf & Gobuster — Web Fuzzing

Herramientas de fuzzing web para descubrimiento de directorios, archivos, subdominios, parámetros y virtual hosts.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## ffuf (Fuzz Faster U Fool)

### Descubrimiento de Directorios
```bash
# Básico
ffuf -u http://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt

# Con extensiones
ffuf -u http://target.com/FUZZ -w wordlist.txt -e .php,.html,.txt,.bak,.old

# Recursivo
ffuf -u http://target.com/FUZZ -w wordlist.txt -recursion -recursion-depth 3

# Filtrar por código de respuesta
ffuf -u http://target.com/FUZZ -w wordlist.txt -mc 200,301,302,403

# Filtrar respuestas por tamaño (eliminar false positives)
ffuf -u http://target.com/FUZZ -w wordlist.txt -fs 4242

# Filtrar por cantidad de palabras
ffuf -u http://target.com/FUZZ -w wordlist.txt -fw 12

# Filtrar por cantidad de líneas
ffuf -u http://target.com/FUZZ -w wordlist.txt -fl 10

# Filtrar por regex en respuesta
ffuf -u http://target.com/FUZZ -w wordlist.txt -fr "not found"

# Excluir códigos
ffuf -u http://target.com/FUZZ -w wordlist.txt -fc 404,403
```

### Fuzzing de Parámetros
```bash
# GET parameters
ffuf -u "http://target.com/page?FUZZ=test" -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt

# GET parameter values
ffuf -u "http://target.com/page?id=FUZZ" -w /usr/share/seclists/Fuzzing/1-1000.txt

# POST data
ffuf -u http://target.com/login -X POST -d "username=admin&password=FUZZ" -w passwords.txt -fc 401

# POST con Content-Type
ffuf -u http://target.com/api -X POST \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","pass":"FUZZ"}' \
  -w passwords.txt
```

### Fuzzing de Subdominios
```bash
# Virtual host discovery (Host header)
ffuf -u http://target.com -H "Host: FUZZ.target.com" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -fs 4242    # Filtrar tamaño de respuesta default

# DNS-based
ffuf -u http://FUZZ.target.com -w subdomains.txt
```

### Fuzzing de Virtual Hosts
```bash
ffuf -u http://<IP> -H "Host: FUZZ.target.htb" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -fs <tamaño_respuesta_default>
```

### Fuzzing de Headers
```bash
# Header values
ffuf -u http://target.com -H "X-Forwarded-For: FUZZ" -w ips.txt

# Header names
ffuf -u http://target.com -H "FUZZ: 127.0.0.1" -w header-names.txt
```

### Multi-wordlist (Clusterbomb)
```bash
# Dos wordlists simultáneas
ffuf -u http://target.com/FUZZ1/FUZZ2 \
  -w wordlist1.txt:FUZZ1 \
  -w wordlist2.txt:FUZZ2

# Brute force login
ffuf -u http://target.com/login -X POST \
  -d "user=USER&pass=PASS" \
  -w users.txt:USER \
  -w passwords.txt:PASS \
  -fc 401
```

### Opciones Avanzadas
```bash
# Rate limiting
ffuf -u http://target.com/FUZZ -w wordlist.txt -rate 100   # 100 req/seg

# Threads
ffuf -u http://target.com/FUZZ -w wordlist.txt -t 50       # 50 threads

# Timeout
ffuf -u http://target.com/FUZZ -w wordlist.txt -timeout 10  # 10 seg

# Cookies
ffuf -u http://target.com/FUZZ -w wordlist.txt -b "session=abc123"

# Auth header
ffuf -u http://target.com/api/FUZZ -w wordlist.txt \
  -H "Authorization: Bearer <token>"

# Proxy (para ver en Burp)
ffuf -u http://target.com/FUZZ -w wordlist.txt -x http://127.0.0.1:8080

# Output
ffuf -u http://target.com/FUZZ -w wordlist.txt -o results.json -of json
ffuf -u http://target.com/FUZZ -w wordlist.txt -o results.csv -of csv
ffuf -u http://target.com/FUZZ -w wordlist.txt -o results.html -of html

# Auto-calibración (detecta y filtra respuestas default automáticamente)
ffuf -u http://target.com/FUZZ -w wordlist.txt -ac

# Modo silencioso
ffuf -u http://target.com/FUZZ -w wordlist.txt -s
```

---

## Gobuster

### Descubrimiento de Directorios (dir)
```bash
# Básico
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt

# Con extensiones
gobuster dir -u http://target.com -w wordlist.txt -x php,html,txt

# Threads y timeout
gobuster dir -u http://target.com -w wordlist.txt -t 50 --timeout 10s

# Status codes
gobuster dir -u http://target.com -w wordlist.txt -s 200,301,302

# Exclude status codes
gobuster dir -u http://target.com -w wordlist.txt -b 404,403

# Con cookies
gobuster dir -u http://target.com -w wordlist.txt -c "session=abc123"

# User-agent custom
gobuster dir -u http://target.com -w wordlist.txt -a "Mozilla/5.0"

# Follow redirects
gobuster dir -u http://target.com -w wordlist.txt -r

# HTTPS sin verificar certificado
gobuster dir -u https://target.com -w wordlist.txt -k

# Output
gobuster dir -u http://target.com -w wordlist.txt -o results.txt

# Proxy
gobuster dir -u http://target.com -w wordlist.txt --proxy http://127.0.0.1:8080

# Headers custom
gobuster dir -u http://target.com -w wordlist.txt -H "Authorization: Bearer <token>"

# Exclude length (filtrar false positives)
gobuster dir -u http://target.com -w wordlist.txt --exclude-length 1234
```

### Descubrimiento de Subdominios (dns)
```bash
# Subdomain bruteforce
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Con resolver custom
gobuster dns -d target.com -w subdomains.txt -r 8.8.8.8

# Show IPs
gobuster dns -d target.com -w subdomains.txt -i

# Wildcard detection
gobuster dns -d target.com -w subdomains.txt --wildcard
```

### Virtual Hosts (vhost)
```bash
gobuster vhost -u http://target.com -w subdomains.txt --append-domain

# Con IP directa
gobuster vhost -u http://<IP> -w subdomains.txt --domain target.htb --append-domain
```

### Fuzzing (fuzz)
```bash
# Similar a ffuf
gobuster fuzz -u http://target.com/FUZZ -w wordlist.txt

# Exclude status
gobuster fuzz -u http://target.com/FUZZ -w wordlist.txt -b 404
```

### S3 Buckets (s3)
```bash
gobuster s3 -w bucket-names.txt
```

---

## Wordlists Recomendadas

```bash
# SecLists (instalar: apt install seclists)
/usr/share/seclists/Discovery/Web-Content/common.txt              # General
/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  # Extensivo
/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt    # Directorios
/usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt          # Archivos
/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt       # Parámetros
/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt        # Subdominios

# Dirb
/usr/share/wordlists/dirb/common.txt
/usr/share/wordlists/dirb/big.txt

# Dirbuster
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

---

## ffuf vs Gobuster — Cuándo Usar Cada Uno

| Aspecto | ffuf | Gobuster |
|---------|------|----------|
| Velocidad | Muy rápido | Rápido |
| Flexibilidad de fuzzing | Superior (multi-position, headers, POST) | Limitado |
| Filtrado | Más opciones (size, words, lines, regex) | Básico |
| Auto-calibración | Sí (`-ac`) | No |
| Subdominios | Vía Host header | Modo DNS dedicado |
| Output formats | JSON, CSV, HTML | Texto |
| Uso recomendado | Fuzzing complejo, parámetros, APIs | Dir/DNS discovery rápido |

**Regla general:** ffuf para fuzzing avanzado y cuando necesitas filtrar. Gobuster para discovery rápido de directorios y DNS.
