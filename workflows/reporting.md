# Reporting & Documentation — Pentesting Deliverables

Guía para documentación durante el engagement y elaboración de informes de pentesting profesionales.

**Fuente:** HTB Academy — Introduction to Documentation and Reporting

---

## Principios de Documentación

### Durante el Engagement

- **Documentar en tiempo real** — no al final. Cada hallazgo, cada comando, cada output
- **Screenshots con timestamps** — evidencia irrefutable
- **Guardar command output** — `| tee output.txt` o herramienta de logging
- **Organizar por fase** — Recon, Enumeration, Exploitation, Post-Exploitation, Privesc

### Estructura de Notas Recomendada

```
engagement/
├── 01_recon/
│   ├── nmap_results/
│   ├── subdomain_enum/
│   └── osint/
├── 02_enumeration/
│   ├── web/
│   ├── smb/
│   └── ad/
├── 03_exploitation/
│   ├── attack_chain/
│   └── individual_findings/
├── 04_post_exploitation/
│   ├── credentials/
│   ├── lateral_movement/
│   └── persistence/
├── 05_evidence/
│   ├── screenshots/
│   └── command_output/
└── 06_reporting/
    ├── draft/
    └── final/
```

---

## Componentes del Informe

### 1. Attack Chain

Demostrar el impacto real de vulnerabilidades combinadas. Un hallazgo Medium + otro Medium pueden = Critical cuando se encadenan.

**Estructura:**
1. Resumen del attack chain (descripción de alto nivel del camino completo)
2. Pasos detallados con evidencia (command output, screenshots)
3. La evidencia puede reutilizarse en los findings individuales

**Ejemplo — Internal Pentest → Domain Compromise:**
```
Responder (LLMNR/NBT-NS spoofing)
    → Hash NTLMv2 capturado
    → Cracking offline → credenciales en texto claro
        → BloodHound enumeration → cuenta con SPN y AdminTo
            → Kerberoasting targeted → cracking del TGS
                → Acceso a servidor → LSA secrets → credenciales de servicio
                    → Local admin en múltiples servers
                        → RDP → usuario con DCSync rights logueado
                            → TGT extraction + Pass-the-Ticket
                                → DCSync → hash del Administrator
                                    → Domain Compromise
```

**Propósito:** Mostrar al cliente que parchear 2-3 vulnerabilidades específicas puede romper toda la cadena mientras trabajan en remediar todos los hallazgos.

---

### 2. Executive Summary

**Audiencia:** La persona que asigna presupuesto. Asumir que NO es técnica.

**Reglas:**

| Hacer | No Hacer |
|-------|----------|
| Ser específico con métricas ("25 ocurrencias") | Recomendar vendors específicos (decir "EDR" no "CrowdStrike") |
| Mantenerlo breve (1.5-2 páginas máximo) | Usar acrónimos técnicos (SNMP, MitM, LLMNR) |
| Describir impacto en términos de negocio | Dedicar espacio a hallazgos menores |
| Recomendar mejoras de proceso, no solo parches | Usar vocabulario rebuscado |
| Estimar esfuerzo de remediación (bajo/medio/alto) | Referenciar secciones técnicas |
| Reconocer lo que hacen bien | Hablar en absolutos ("nunca", "siempre") |
| Usar calificadores ("parece que", "indicaría que") | Insinuar que no han hecho nada |

**Vocabulario para Audiencia No Técnica:**

| Término Técnico | Alternativa Accesible |
|-----------------|----------------------|
| VPN, SSH | Protocolo para administración remota segura |
| SSL/TLS | Tecnología que facilita navegación web segura |
| Hash | Resultado de un algoritmo para validar integridad |
| Password Spraying | Ataque que prueba una contraseña fácil contra muchas cuentas |
| Password Cracking | Proceso offline que convierte forma criptográfica a texto legible |
| Buffer overflow / deserialización | Ataque que resultó en ejecución remota de comandos |
| OSINT | Búsqueda de datos públicos usando buscadores y fuentes abiertas |
| SQL injection / XSS | Vulnerabilidad donde se acepta input sin sanitizar |

**Anatomía:**
1. Reconocer lo que hacen bien
2. Categorizar hallazgos por naturaleza del riesgo
3. Identificar el tema general (ej: config management inmaduro)
4. Describir impacto en términos de negocio
5. No hablar en absolutos
6. No insinuar negligencia

---

### 3. Summary of Recommendations

Organizar en corto, mediano y largo plazo:

| Plazo | Ejemplo |
|-------|---------|
| **Corto** | Parchear vulnerabilidades específicas, cambiar credenciales débiles |
| **Mediano** | Implementar templates de hardening, configurar monitoring |
| **Largo** | Revisar procesos de patch management, pentests periódicos, security awareness |

- Cada recomendación vinculada a un hallazgo específico
- Un hallazgo puede tener recomendación de corto Y largo plazo
- Priorizar — "When everything is important, nothing is important"

---

### 4. Findings (Hallazgos Detallados)

Cada finding debe incluir:

```
Título del Hallazgo
├── Severidad (Critical/High/Medium/Low/Informational)
├── CVSS Score (si aplica)
├── CWE / CVE (si aplica)
├── Descripción
│   ├── Qué es la vulnerabilidad
│   └── Por qué es un riesgo
├── Hosts / URLs Afectados
├── Evidencia
│   ├── Steps to Reproduce (paso a paso reproducible)
│   ├── Command output
│   └── Screenshots con timestamps
├── Impacto
│   ├── Técnico
│   └── Business impact
└── Remediación
    ├── Acción específica
    ├── Referencias (vendor advisory, hardening guides)
    └── Esfuerzo estimado
```

**Priorización de hallazgos:**
- Filtrar ruido de escaneos → enfocarse en RCE, data disclosure, lateral movement
- Consolidar hallazgos menores en categorías (ej: 35 variaciones SSL/TLS → una categoría)
- Apoyarse en mentores para validar si algo es false positive

---

### 5. Appendices

**Estáticos (siempre incluir):**

| Apéndice | Contenido |
|----------|-----------|
| Scope | URLs, rangos de red, facilities |
| Methodology | Proceso repetible (OWASP, PTES, etc.) |
| Severity Ratings | Criterios de severidad usados |
| Biographies | Qualificaciones del consultor |

**Dinámicos (según el assessment):**

| Apéndice | Cuándo Incluir |
|----------|----------------|
| Exploitation Attempts & Payloads | Siempre que se dejen artefactos (incluir hashes y ubicaciones) |
| Compromised Credentials | Si se comprometieron cuentas |
| Configuration Changes | Cualquier cambio realizado en el entorno |
| Additional Affected Scope | Listas largas de hosts que no caben en el hallazgo |
| Information Gathering / OSINT | Para externos: whois, subdominios, emails, breach data |
| Domain Password Analysis | Si se obtuvo NTDS: stats de cracking con DPAT |

---

## Diferencias por Tipo de Assessment

| Tipo | Características del Informe |
|------|----------------------------|
| **Internal Pentest** | Attack chain completa, todos los apéndices, domain password analysis |
| **External (sin compromise)** | Enfoque en OSINT, servicios expuestos. Sin attack chain |
| **External (con compromise)** | Similar a internal + datos OSINT |
| **Web Application** | Executive Summary + Findings centrados en OWASP Top 10 |
| **Physical / Red Team / SE** | Formato más narrativo |

---

## Herramientas de Documentación

### Notetaking
```
- CherryTree        → Hierarchical, popular en OSCP
- Obsidian          → Markdown, wikilinks, graph view
- Notion            → Web-based, templates
- Joplin            → Open source, markdown
```

### Logging Automático
```bash
# Script wrapper para logging
script -a engagement.log

# Tmux logging
# En .tmux.conf: set -g history-limit 50000

# Herramientas dedicadas
- Ghostwriter       → Report management platform
- PlexTrac          → Commercial pentest reporting
- Pwndoc            → Open source report generator
- SysReptor         → Open source pentest reporting
```

### Evidence
```
- Flameshot          → Screenshots con anotaciones
- ShareX             → Screenshots avanzados (Windows)
- asciinema          → Grabar terminal sessions
- OBS                → Grabar video de exploits complejos
```

---

## Checklist de Calidad del Informe

```
□ Executive Summary comprensible para no-técnicos
□ Attack chain documenta el path completo
□ Cada finding tiene steps to reproduce verificables
□ Screenshots con timestamps
□ Métricas específicas (no "varios", sino "25 ocurrencias")
□ Recomendaciones vinculadas a findings
□ Recomendaciones organizadas por plazo (corto/mediano/largo)
□ Sin acrónimos sin explicar en Executive Summary
□ Sin vendors específicos en recomendaciones
□ Severity ratings justificables
□ Scope claramente documentado
□ Methodology descrita
□ Credenciales comprometidas listadas
□ Artefactos dejados en el entorno documentados
□ Revisión por peer antes de entregar
```

---

## Tips

- **El informe es el entregable principal** — es por lo que paga el cliente. Todo lo demás (el hacking) es el medio
- **Documentar mientras hackeas, no después** — la memoria es unreliable, los logs no
- **Template por tipo de assessment** — tener templates listos ahorra horas
- **Peer review es obligatorio** — otro pentester revisa antes de entregar
- **Recibir feedback con mente abierta** — el informe es un producto que el cliente pagó
- **Mantener una base de findings** — reutilizar descripciones y remediaciones entre engagements (personalizando evidencia)
