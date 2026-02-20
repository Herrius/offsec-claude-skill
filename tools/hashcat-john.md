# Hashcat & John the Ripper — Password Cracking

Herramientas de cracking de contraseñas. Hashcat usa GPU para máxima velocidad, John es más versátil y flexible con formatos.

**Contexto:** Uso en pentesting autorizado, CTFs, y laboratorios de seguridad.

---

## Hashcat

### Identificar el Hash
```bash
# Herramientas de identificación
hashid '<hash>'
hash-identifier
hashcat --identify hash.txt

# Referencia rápida de modos comunes
# -m 0     = MD5
# -m 100   = SHA-1
# -m 1400  = SHA-256
# -m 1700  = SHA-512
# -m 1000  = NTLM
# -m 3200  = bcrypt
# -m 1800  = sha512crypt ($6$)
# -m 500   = md5crypt ($1$)
# -m 5600  = NetNTLMv2
# -m 5500  = NetNTLMv1
# -m 13100 = Kerberos 5 TGS-REP (Kerberoasting)
# -m 18200 = Kerberos 5 AS-REP (AS-REP Roasting)
# -m 22000 = WPA-PBKDF2-PMKID+EAPOL
# -m 16800 = WPA-PMKID
# -m 11600 = 7-Zip
# -m 13600 = WinZip
# -m 13400 = KeePass
# -m 1500  = DES (Unix)
# -m 3000  = LM
# -m 7500  = Kerberos 5 AS-REQ Pre-Auth
```

### Modos de Ataque
```bash
# -a 0: Dictionary attack
hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt

# -a 1: Combinator (combina dos wordlists)
hashcat -m 0 -a 1 hash.txt wordlist1.txt wordlist2.txt

# -a 3: Brute force / mask attack
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a    # 6 chars, todos
hashcat -m 0 -a 3 hash.txt ?u?l?l?l?d?d     # Ulll00

# -a 6: Hybrid wordlist + mask
hashcat -m 0 -a 6 hash.txt wordlist.txt ?d?d?d   # palabra + 3 dígitos

# -a 7: Hybrid mask + wordlist
hashcat -m 0 -a 7 hash.txt ?d?d?d wordlist.txt   # 3 dígitos + palabra
```

### Charsets para Masks
```
?l = abcdefghijklmnopqrstuvwxyz
?u = ABCDEFGHIJKLMNOPQRSTUVWXYZ
?d = 0123456789
?s = !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
?a = ?l?u?d?s (todos)
?b = 0x00-0xff (binary)

# Custom charset
hashcat -m 0 -a 3 hash.txt -1 ?l?d ?1?1?1?1?1?1  # lowercase + digits
hashcat -m 0 -a 3 hash.txt -1 abc -2 123 ?1?1?2?2  # custom sets
```

### Rules
```bash
# Usar rules predefinidas
hashcat -m 0 -a 0 hash.txt wordlist.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 0 -a 0 hash.txt wordlist.txt -r /usr/share/hashcat/rules/rockyou-30000.rule
hashcat -m 0 -a 0 hash.txt wordlist.txt -r /usr/share/hashcat/rules/OneRuleToRuleThemAll.rule

# Múltiples rules (se combinan)
hashcat -m 0 -a 0 hash.txt wordlist.txt -r rule1.rule -r rule2.rule

# Generar reglas con debug
hashcat -m 0 -a 0 hash.txt wordlist.txt -r rules.rule --debug-mode=1 --debug-file=matched.txt
```

### Opciones Importantes
```bash
# Forzar tipo de dispositivo
hashcat -D 1 ...    # CPU only
hashcat -D 2 ...    # GPU only

# Workload profile
hashcat -w 3 ...    # High performance (puede congelar desktop)
hashcat -w 4 ...    # Nightmare (solo headless)

# Mostrar resultados crackeados
hashcat -m 0 hash.txt --show

# Guardar sesión y restaurar
hashcat -m 0 -a 0 hash.txt wordlist.txt --session=mi_sesion
hashcat --session=mi_sesion --restore

# Optimized kernels (más rápido, limita longitud a 32 chars)
hashcat -m 0 -a 0 hash.txt wordlist.txt -O

# Output file
hashcat -m 0 -a 0 hash.txt wordlist.txt -o cracked.txt

# Output format
hashcat -m 0 -a 0 hash.txt wordlist.txt -o cracked.txt --outfile-format=2  # solo password

# Benchmark
hashcat -b
hashcat -b -m 1000   # Benchmark NTLM específicamente

# Potfile (donde guarda resultados automáticamente)
# ~/.local/share/hashcat/hashcat.potfile
```

### Escenarios Comunes

**NTLM (Windows):**
```bash
hashcat -m 1000 -a 0 ntlm_hashes.txt /usr/share/wordlists/rockyou.txt -r best64.rule
```

**NetNTLMv2 (Responder capture):**
```bash
hashcat -m 5600 -a 0 netntlmv2.txt /usr/share/wordlists/rockyou.txt
```

**Kerberoasting:**
```bash
hashcat -m 13100 -a 0 tgs_hashes.txt /usr/share/wordlists/rockyou.txt -r best64.rule
```

**AS-REP Roasting:**
```bash
hashcat -m 18200 -a 0 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
```

**Linux shadow ($6$ sha512crypt):**
```bash
hashcat -m 1800 -a 0 shadow_hashes.txt /usr/share/wordlists/rockyou.txt
```

**WPA/WPA2:**
```bash
# Convertir capture a hashcat format
hcxpcapngtool capture.pcapng -o hash.hc22000
hashcat -m 22000 -a 0 hash.hc22000 /usr/share/wordlists/rockyou.txt
```

**KeePass:**
```bash
# Extraer hash con keepass2john o john
keepass2john database.kdbx > keepass_hash.txt
# Limpiar formato para hashcat
hashcat -m 13400 -a 0 keepass_hash.txt /usr/share/wordlists/rockyou.txt
```

---

## John the Ripper

### Uso Básico
```bash
# Auto-detect format
john hash.txt

# Especificar formato
john --format=raw-md5 hash.txt
john --format=raw-sha256 hash.txt
john --format=NT hash.txt
john --format=bcrypt hash.txt

# Wordlist
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Rules
john --wordlist=wordlist.txt --rules=All hash.txt
john --wordlist=wordlist.txt --rules=Jumbo hash.txt

# Incremental (brute force)
john --incremental hash.txt
john --incremental=Digits hash.txt    # Solo dígitos

# Mostrar contraseñas crackeadas
john --show hash.txt

# Listar formatos disponibles
john --list=formats | grep -i <tipo>
```

### Extractores de Hash (john2*)
```bash
# Archivos protegidos con password
zip2john file.zip > zip_hash.txt
rar2john file.rar > rar_hash.txt
pdf2john file.pdf > pdf_hash.txt
office2john file.docx > office_hash.txt

# SSH keys
ssh2john id_rsa > ssh_hash.txt

# KeePass
keepass2john database.kdbx > keepass_hash.txt

# GPG
gpg2john private.key > gpg_hash.txt

# 7z
7z2john file.7z > 7z_hash.txt

# Luego crackear
john --wordlist=/usr/share/wordlists/rockyou.txt <hash_file>
```

### Opciones Avanzadas
```bash
# Fork (paralelismo CPU)
john --fork=4 --wordlist=rockyou.txt hash.txt

# Session management
john --session=mi_sesion --wordlist=rockyou.txt hash.txt
john --restore=mi_sesion

# Mask mode (similar a hashcat)
john --mask='?u?l?l?l?d?d' hash.txt

# Markov mode
john --markov hash.txt

# External mode
john --external=Filter_Alpha hash.txt

# Potfile
# ~/.john/john.pot
```

---

## Hashcat vs John — Cuándo Usar Cada Uno

| Aspecto | Hashcat | John |
|---------|---------|------|
| Velocidad (GPU) | Superior | Limitado |
| Formatos soportados | Muchos | Más (especialmente archivos) |
| Extractores (zip2john, etc.) | No incluidos | Incluidos |
| Rules | Potentes, propias | Compatibles con hashcat |
| Masks | Nativo | Soportado |
| Mejor para | Hashes de red/AD, WPA, bulk cracking | Archivos protegidos, formatos raros |

**Workflow típico:**
1. Identificar hash con `hashid` o `hashcat --identify`
2. Si es un archivo protegido → `*2john` para extraer hash
3. Si necesitas GPU speed → Hashcat
4. Si es formato raro o necesitas extraer → John
5. Empezar con `rockyou.txt`, luego agregar rules
6. Si dictionary no funciona → mask/brute force

---

## Tips

- **Siempre probar sin rules primero** — rockyou.txt solo encuentra mucho
- **Rules recomendadas:** `best64.rule` (rápido) → `OneRuleToRuleThemAll.rule` (exhaustivo)
- **Wordlists combinadas:** `cat rockyou.txt custom_words.txt | sort -u > combined.txt`
- **Para CTFs:** Probar `rockyou.txt` primero, luego CeWL para generar wordlist del sitio
- **Hash de sitio web:** Probar rainbow tables online primero (CrackStation, hashes.org)
- **NTLM es rápido:** Puedes probar masks extensivas porque hashcat crackea NTLM muy rápido
