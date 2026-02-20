# BloodHound — Active Directory Attack Path Analysis

Herramienta de análisis de relaciones en Active Directory. Mapea rutas de ataque desde cualquier usuario hasta Domain Admin mediante grafos.

**Contexto:** Uso en pentesting autorizado de AD, CTFs, y laboratorios de seguridad.

---

## Arquitectura

```
SharpHound/bloodhound-python (Collector)
        ↓ genera JSON/ZIP
BloodHound (GUI + Neo4j)
        ↓ analiza grafos
Rutas de ataque identificadas
```

---

## Collectors (Recolección de Datos)

### SharpHound (desde Windows, in-domain)
```powershell
# Descarga: github.com/BloodHoundAD/SharpHound

# Recolección completa
.\SharpHound.exe -c All

# Recolección con opciones
.\SharpHound.exe -c All --domain target.local --ldapusername user --ldappassword pass

# Collection methods individuales
.\SharpHound.exe -c DCOnly          # Solo DC (menos ruidoso)
.\SharpHound.exe -c Session         # Solo sesiones activas
.\SharpHound.exe -c Group           # Solo membresías de grupo
.\SharpHound.exe -c ACL             # Solo ACLs
.\SharpHound.exe -c Trusts          # Solo trusts entre dominios

# Loop de sesiones (recolectar periódicamente)
.\SharpHound.exe -c Session --loop --loopduration 02:00:00

# Excluir domain controllers (menos ruidoso)
.\SharpHound.exe -c All --excludedcs

# Stealth mode
.\SharpHound.exe -c All --stealth

# Output a directorio específico
.\SharpHound.exe -c All --outputdirectory C:\Users\Public\

# PowerShell version
Import-Module .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All
```

### bloodhound-python (desde Linux, remoto)
```bash
# Instalar
pip install bloodhound

# Recolección básica
bloodhound-python -u 'user' -p 'password' -d target.local -ns <DC_IP> -c All

# Con hash NTLM
bloodhound-python -u 'user' --hashes ':<NTLM_hash>' -d target.local -ns <DC_IP> -c All

# DNS resolution manual
bloodhound-python -u 'user' -p 'password' -d target.local -dc dc01.target.local -ns <DC_IP> -c All

# Solo DCOnly (menos ruidoso)
bloodhound-python -u 'user' -p 'password' -d target.local -ns <DC_IP> -c DCOnly

# Con Kerberos
bloodhound-python -u 'user' -p 'password' -d target.local -ns <DC_IP> -c All --auth-method kerberos -k
```

### rusthound (alternativa rápida)
```bash
# Más rápido que bloodhound-python
rusthound -d target.local -u 'user' -p 'password' -i <DC_IP> --old-bloodhound
```

---

## BloodHound GUI

### Setup
```bash
# BloodHound CE (Community Edition — nueva versión)
# Docker compose:
curl -L https://ghst.ly/getbhce | docker compose -f - up

# BloodHound Legacy (con Neo4j)
# Iniciar Neo4j
sudo neo4j start
# Default creds: neo4j/neo4j → cambiar en primer login
# Abrir BloodHound GUI
bloodhound

# Importar datos
# Drag & drop los archivos JSON/ZIP del collector
```

### Queries Pre-built Esenciales

**Rutas a Domain Admin:**
```
Find Shortest Paths to Domain Admins
Find All Paths to Domain Admins (más exhaustivo)
Shortest Paths to High Value Targets
```

**Kerberos:**
```
List All Kerberoastable Accounts
Find AS-REP Roastable Users
Find Accounts with Unconstrained Delegation
Find Accounts with Constrained Delegation
```

**ACL Abuse:**
```
Find Principals with DCSync Rights
Find Users with GenericAll on other Users
Find Groups with AdminTo rights
Find Objects where Domain Users have GenericAll
```

**Sesiones:**
```
Find Computers where Domain Users are Local Admin
Find Computers where Domain Admins are logged in
Sessions of High Value Targets
```

**Trusts:**
```
Map Domain Trusts
Find Foreign Group Memberships
```

### Custom Cypher Queries

```cypher
# Usuarios con password que no expira
MATCH (u:User {pwdneverexpires: true}) RETURN u.name

# Usuarios que no requieren Kerberos pre-auth (AS-REP roastable)
MATCH (u:User {dontreqpreauth: true}) RETURN u.name

# Computadoras con unconstrained delegation
MATCH (c:Computer {unconstraineddelegation: true}) RETURN c.name

# Usuarios con SPN set (Kerberoastable)
MATCH (u:User) WHERE u.hasspn = true RETURN u.name

# Shortest path desde owned user a DA
MATCH p=shortestPath((u:User {owned: true})-[*1..]->(g:Group {name: "DOMAIN ADMINS@TARGET.LOCAL"})) RETURN p

# Usuarios con GenericAll sobre otro objeto
MATCH p=(u:User)-[:GenericAll]->(target) RETURN u.name, target.name

# Rutas a través de ACLs abusables
MATCH p=shortestPath((u:User)-[:GenericAll|GenericWrite|WriteOwner|WriteDacl|Owns|ForceChangePassword*1..]->(target:User {admincount: true})) RETURN p

# GPO que afectan a máquinas con sesiones de DA
MATCH (g:GPO)-[:GpLink]->(ou:OU)-[:Contains*1..]->(c:Computer)<-[:HasSession]-(u:User)-[:MemberOf*1..]->(da:Group {name: "DOMAIN ADMINS@TARGET.LOCAL"}) RETURN g.name, c.name

# Encontrar rutas via ADCS
MATCH p=shortestPath((u:User)-[*1..]->(t:GPO)) WHERE any(r in relationships(p) WHERE type(r) = "ADCSESC1") RETURN p
```

### Marcar Nodos

```
# En la GUI, click derecho sobre un nodo:
- Mark as Owned      → Has comprometido este objeto
- Mark as High Value → Objetivo de interés
```

---

## Interpretación de Relaciones (Edges)

### Relaciones Abusables (Attack Paths)

| Relación | Significado | Abuso |
|----------|-------------|-------|
| **MemberOf** | Es miembro del grupo | Hereda permisos del grupo |
| **AdminTo** | Es admin local de | PSExec, WMI, RDP |
| **HasSession** | Tiene sesión activa en | Robar credenciales con Mimikatz |
| **GenericAll** | Control total sobre | Cambiar password, agregar a grupo, write SPN |
| **GenericWrite** | Puede modificar atributos | Targeted Kerberoasting, Shadow Credentials |
| **WriteOwner** | Puede cambiar owner | Tomar ownership → WriteDACL → GenericAll |
| **WriteDACL** | Puede modificar ACL | Otorgarse GenericAll |
| **ForceChangePassword** | Puede cambiar password | Cambiar password sin conocer la actual |
| **Owns** | Es propietario de | WriteDACL implícito |
| **CanRDP** | Puede hacer RDP | Acceso interactivo |
| **CanPSRemote** | Puede hacer PS Remoting | PowerShell remoto |
| **ExecuteDCOM** | Puede ejecutar DCOM | Ejecución remota |
| **AllowedToDelegate** | Delegación constrained | Impersonar usuarios |
| **AllowedToAct** | RBCD configurado | Resource-Based Constrained Delegation |
| **HasSIDHistory** | Tiene SID en historial | Puede tener acceso legacy |
| **DCSync** | Derechos de DCSync | Dump de todos los hashes del dominio |
| **AddMember** | Puede agregar miembros | Agregar cuenta a grupo privilegiado |
| **ADCSESC1-8** | Misconfigs de ADCS | Certificate abuse para escalar |

---

## Workflow Típico de BloodHound

```
1. COLLECT: Ejecutar SharpHound/bloodhound-python
2. IMPORT:  Drag & drop ZIP en BloodHound GUI
3. MARK:    Marcar usuario comprometido como "Owned"
4. QUERY:   "Shortest Paths from Owned Principals"
5. ANALYZE: Identificar la ruta más corta/viable
6. EXPLOIT: Seguir la cadena de abuso
7. REPEAT:  Marcar nuevos nodos como Owned, buscar nuevas rutas
```

---

## Tips

- **Siempre recolectar con `-c All`** — la información que no recolectas es la que necesitarás después
- **Sesiones son volátiles** — ejecutar loop de recolección de sesiones si es posible
- **Marcar owned nodes** — las queries de "shortest path from owned" son las más valiosas
- **No ignorar edges indirectos** — GenericWrite → Targeted Kerberoasting → crack password → nuevo acceso
- **ADCS es oro** — si hay Certificate Authority, las rutas ESC1-ESC8 son frecuentemente la vía más fácil
- **Combinar con certipy** — BloodHound muestra las rutas, certipy las explota
- **Export queries** — guardar custom queries que funcionan para reusar en otros engagements
