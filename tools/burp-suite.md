# Burp Suite — Web Application Security Testing

Plataforma integrada de testing de seguridad web. Proxy de interceptación, scanner, repeater, intruder, y extensiones.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## Setup Inicial

### Proxy Configuration
```
Browser → Proxy: 127.0.0.1:8080 → Burp → Target
```

**FoxyProxy (recomendado):**
- Crear perfil "Burp" con proxy `127.0.0.1:8080`
- Alternar entre Burp proxy y conexión directa

**Certificado HTTPS:**
1. Con proxy activo, ir a `http://burp`
2. Descargar CA Certificate
3. Importar en browser: Settings → Certificates → Import → Trust for websites

### Scope Configuration
```
Target → Scope → Add:
- Protocol: Any
- Host: target.com (o IP)
- Port: Any
- File: ^/.*

Project options → Out-of-scope → Drop all out-of-scope
```

---

## Proxy — Interceptación de Tráfico

### Intercept
```
Proxy → Intercept → Intercept is on/off

Acciones sobre request interceptada:
- Forward          → Enviar al servidor
- Drop             → Descartar
- Send to Repeater → Para testing manual (Ctrl+R)
- Send to Intruder → Para fuzzing/brute force (Ctrl+I)
- Send to Decoder  → Para encoding/decoding
```

### Match and Replace (modificar tráfico en vuelo)
```
Proxy → Options → Match and Replace

Ejemplos útiles:
- Request header: User-Agent → custom
- Request header: agregar X-Forwarded-For: 127.0.0.1
- Response header: remover Content-Security-Policy
- Response body: reemplazar "hidden" por "text" en forms
- Response header: remover X-Frame-Options (para clickjacking testing)
```

### HTTP History
```
Proxy → HTTP history

Filtros útiles:
- Filter by MIME type (HTML, Script, JSON)
- Filter by status code
- Filter by search term
- Filter by scope
- Highlight y comment requests interesantes
```

---

## Repeater — Testing Manual

```
Ctrl+R desde cualquier request → Repeater

Workflow:
1. Enviar request original
2. Modificar parámetros
3. Send y comparar respuesta
4. Iterar hasta encontrar vulnerabilidad

Tips:
- Usar tabs para comparar variaciones
- Renombrar tabs por test type
- Follow redirects: toggle en settings
- Auto-update Content-Length: habilitado por default
```

### Testing Patterns en Repeater

**SQLi Testing:**
```
Original: id=1
Test:     id=1'          → Error = posible SQLi
Test:     id=1 OR 1=1--  → Más data = confirmado
Test:     id=1 UNION SELECT NULL,NULL-- → Determinar columnas
```

**XSS Testing:**
```
Original: search=test
Test:     search=<script>alert(1)</script>
Test:     search="><img src=x onerror=alert(1)>
Test:     search=javascript:alert(1)
```

**SSTI Testing:**
```
Original: name=test
Test:     name={{7*7}}     → Si muestra 49 = SSTI
Test:     name=${7*7}      → Variante
Test:     name=<%= 7*7 %>  → ERB
```

**Command Injection:**
```
Original: ip=127.0.0.1
Test:     ip=127.0.0.1;whoami
Test:     ip=127.0.0.1|whoami
Test:     ip=127.0.0.1`whoami`
```

---

## Intruder — Fuzzing y Brute Force

### Attack Types

**Sniper:** Un payload set, una posición a la vez
```
Posiciones: §username§ y §password§
Payloads: [admin, root, test]
→ Prueba cada payload en cada posición secuencialmente
Uso: Testing individual de cada parámetro
```

**Battering Ram:** Un payload set, todas las posiciones simultáneamente
```
Posiciones: §user§ y §pass§ (mismo valor en ambas)
Payloads: [admin, test]
→ user=admin&pass=admin, user=test&pass=test
Uso: Cuando usuario = password
```

**Pitchfork:** Múltiples payload sets, en paralelo (1:1)
```
Posición 1: §user§ → [admin, root, test]
Posición 2: §pass§ → [admin123, toor, test123]
→ admin/admin123, root/toor, test/test123
Uso: Credential stuffing con pares conocidos
```

**Cluster Bomb:** Múltiples payload sets, todas las combinaciones
```
Posición 1: §user§ → [admin, root]
Posición 2: §pass§ → [123, 456, 789]
→ admin/123, admin/456, admin/789, root/123, root/456, root/789
Uso: Brute force completo
```

### Payload Types
```
Simple list         → Lista de valores
Runtime file        → Cargar desde archivo
Numbers             → Secuencia numérica (from, to, step)
Dates               → Rango de fechas
Brute forcer        → Generación de caracteres
Null payloads       → Requests sin modificar (rate testing)
Character frobber   → Modifica un char a la vez
Bit flipper         → Flip bits (crypto testing)
Username generator  → Variaciones de usernames
```

### Payload Processing
```
Add prefix/suffix
Encode (URL, Base64, HTML)
Hash (MD5, SHA)
Match/Replace
Reverse
Case modification
```

### Grep Match (detectar resultados)
```
Intruder → Options → Grep - Match:
- "Invalid password"  → Login failures
- "Welcome"           → Login success
- "error"             → Errors
- Flag format regex   → CTF flag detection
```

---

## Decoder — Encoding/Decoding

```
Soporta:
- URL encoding/decoding
- HTML encoding/decoding
- Base64 encode/decode
- Hex encode/decode
- Binary
- Gzip
- Hash (MD5, SHA-1, SHA-256, SHA-512)

Workflow:
1. Paste encoded string
2. Decode as → URL / Base64 / etc.
3. Se pueden encadenar múltiples decodings
4. Smart Decode intenta detectar automáticamente
```

---

## Comparer — Diff de Responses

```
1. Enviar dos responses a Comparer (click derecho → Send to Comparer)
2. Comparer → Words o Bytes
3. Identifica diferencias exactas entre responses

Uso:
- Comparar respuesta con/sin autenticación
- Identificar qué cambia con diferentes payloads
- Detectar blind injection por diferencias sutiles
```

---

## Extensiones Esenciales (BApp Store)

```
# BApp Store → buscar e instalar

Autorize          → Testing automático de autorización (IDOR/privesc)
Logger++          → Logging avanzado de todas las requests
Param Miner       → Descubrir parámetros ocultos
Active Scan++     → Mejora scanner activo
JSON Beautifier   → Formato legible de JSON
JWT Editor        → Manipular tokens JWT
Turbo Intruder    → Intruder más rápido (Python scripting)
Hackvertor        → Encoding/decoding avanzado
Upload Scanner    → Testing de file upload
Collaborator Everywhere → Insertar payloads Collaborator en headers
Software Vulnerability Scanner → CVE detection
```

### Autorize (IDOR/Authorization Testing)
```
1. Instalar extensión
2. Configurar cookie/header de usuario low-priv
3. Navegar como admin
4. Autorize repite cada request con cookies de low-priv
5. Compara respuestas → highlight diferencias de autorización
```

### Turbo Intruder
```python
# Más rápido que Intruder standard
# Click derecho → Extensions → Turbo Intruder → Send to Turbo Intruder

# Ejemplo: Race condition
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                          concurrentConnections=30,
                          requestsPerConnection=100,
                          pipeline=False)
    for i in range(30):
        engine.queue(target.req)

def handleResponse(req, interesting):
    if interesting:
        table.add(req)
```

---

## Scanner (Pro only)

```
# Passive Scan: automático sobre tráfico proxy
# Active Scan: envía payloads al target

Dashboard → New Scan:
- Crawl and Audit
- Crawl only
- Audit selected items

Scan configurations:
- Audit checks → seleccionar tipos de vuln
- Crawl settings → profundidad, velocidad
- Resource pool → controlar carga

Reportes:
Target → Issues → right-click → Report issues
```

---

## Tips y Shortcuts

```
Ctrl+R    → Send to Repeater
Ctrl+I    → Send to Intruder
Ctrl+U    → URL encode selection
Ctrl+Shift+U → URL decode selection
Ctrl+B    → Base64 encode
Ctrl+Shift+B → Base64 decode
Ctrl+Space → Send request (en Repeater)
Ctrl+T    → New tab (Repeater)
```

### Workflow Recomendado

```
1. SCOPE:    Configurar scope del target
2. CRAWL:    Navegar manualmente con proxy ON → mapear aplicación
3. ANALYZE:  Revisar HTTP History → identificar puntos interesantes
4. TEST:     Enviar requests a Repeater → testing manual
5. FUZZ:     Usar Intruder para parámetros que necesitan fuzzing
6. SCAN:     Active scan en endpoints interesantes (Pro)
7. REPORT:   Documentar findings con evidencia
```

### HTTP History — Qué Buscar

```
- Endpoints con parámetros (id=, user=, file=, url=, path=)
- Tokens en URL o cookies
- API endpoints (/api/v1/, /graphql)
- Headers interesantes (X-Forwarded-For, Authorization)
- Responses con info sensible (emails, IPs internas, stack traces)
- Redirects (302) con URLs manipulables
- File uploads y downloads
- WebSocket connections
```
