# Security Policy

## 🔒 Sicherheit bei ORION Architekt-AT

Die Sicherheit von ORION Architekt-AT hat höchste Priorität. Wir nehmen alle Sicherheitsbedenken ernst und schätzen die Bemühungen der Security Community.

## 📋 Unterstützte Versionen

Wir bieten Security-Updates für folgende Versionen:

| Version | Unterstützt          |
| ------- | -------------------- |
| 3.0.x   | ✅ Aktiv unterstützt |
| 2.x.x   | ❌ End of Life       |
| 1.x.x   | ❌ End of Life       |
| < 1.0   | ❌ End of Life       |

## 🚨 Sicherheitslücke melden

### ⚠️ WICHTIG: Keine öffentlichen Issues für Security-Probleme!

Wenn Sie eine Sicherheitslücke entdecken, **erstellen Sie KEIN öffentliches GitHub Issue**.

### Meldeprozess

1. **Email an Security Team**
   - Email: security@orion-architekt.at
   - Subject: `[SECURITY] Beschreibung der Lücke`
   - PGP Key (optional): [Link zum PGP Key]

2. **Erforderliche Informationen**
   ```
   - Typ der Sicherheitslücke
   - Vollständige Pfade der betroffenen Quellcode-Dateien
   - Ort des betroffenen Codes (tag/branch/commit oder URL)
   - Schritte zur Reproduktion
   - Proof-of-Concept oder Exploit-Code (falls vorhanden)
   - Impact der Sicherheitslücke
   - Mögliche Lösungsvorschläge (optional)
   ```

3. **Response Zeit**
   - **Initiale Antwort:** Innerhalb von 48 Stunden
   - **Status Update:** Wöchentlich bis zur Lösung
   - **Patch Release:** Abhängig von Severity (siehe unten)

### Severity Levels

| Level | Beschreibung | Response Zeit |
|-------|--------------|---------------|
| **Critical** | RCE, SQL Injection, Auth Bypass | 24-48 Stunden |
| **High** | XSS, CSRF, Privilege Escalation | 7 Tage |
| **Medium** | Information Disclosure, DoS | 30 Tage |
| **Low** | Kleinere Sicherheitsprobleme | 90 Tage |

## 🛡️ Sicherheitsmaßnahmen

### Implementierte Schutzmaßnahmen

#### 1. Authentication & Authorization

```python
# JWT-basierte Authentifizierung
- Token Expiration: 24 Stunden
- Refresh Token: 7 Tage
- Password Hashing: bcrypt (cost factor 12)
- MFA Support: TOTP (optional)
```

#### 2. Input Validation

```python
# FastAPI Pydantic Models für alle Inputs
- Type Validation
- Range Checks
- Regex Patterns
- SQL Injection Prevention (SQLAlchemy ORM)
```

#### 3. API Security

```python
# Rate Limiting
- Global: 100 requests/minute
- Per User: 50 requests/minute
- Authentication: 5 attempts/15 minutes

# CORS Configuration
- Whitelist-basiert
- Credentials: True (nur für vertrauenswürdige Origins)
- Methods: GET, POST, PUT, DELETE

# Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: default-src 'self'
```

#### 4. Database Security

```python
# PostgreSQL
- Encrypted Connections (SSL/TLS)
- Prepared Statements (SQLAlchemy)
- Row-Level Security (RLS)
- Audit Logging aktiviert

# Backups
- Encrypted at rest (AES-256)
- Encrypted in transit (TLS 1.3)
- 30-day retention
- Daily backups + WAL archiving
```

#### 5. Secrets Management

```python
# Keine Secrets im Code!
- Umgebungsvariablen (.env)
- Kubernetes Secrets (Production)
- Vault Integration (optional)

# Secret Rotation
- JWT Secrets: 90 Tage
- Database Passwords: 90 Tage
- API Keys: Nach Bedarf
```

#### 6. Dependency Management

```python
# Automated Security Scanning
- GitHub Dependabot aktiviert
- Daily vulnerability scans
- Automated PR creation für Updates

# Tools
- safety check (Python dependencies)
- bandit (SAST für Python)
- OWASP Dependency-Check
```

### Sicherheits-Audits

#### Automatisierte Scans

```bash
# SAST (Static Application Security Testing)
bandit -r . -f json -o security-report.json

# Dependency Scanning
safety check --json

# Container Scanning
trivy image orion-architekt-at:latest
```

#### Regelmäßige Reviews

- **Code Reviews:** Jeder Pull Request
- **Security Reviews:** Vierteljährlich
- **Penetration Tests:** Jährlich (externe Firma)
- **Dependency Updates:** Wöchentlich

## 🔐 Best Practices für Contributors

### 1. Secrets niemals committen

```bash
# .gitignore enthält:
.env
.env.local
*.key
*.pem
credentials.json
secrets/
```

### 2. Input Validation

```python
# Immer validieren!
from pydantic import BaseModel, Field, validator

class CalculationInput(BaseModel):
    thickness: float = Field(gt=0, le=2.0)  # 0 < x <= 2.0
    lambda_value: float = Field(gt=0, le=10.0)

    @validator('thickness')
    def validate_thickness(cls, v):
        if v > 2.0:
            raise ValueError("Dicke über 2m unrealistisch")
        return v
```

### 3. SQL Injection Prevention

```python
# ✅ RICHTIG (SQLAlchemy ORM)
user = session.query(User).filter(User.email == email).first()

# ❌ FALSCH (String Interpolation)
# query = f"SELECT * FROM users WHERE email = '{email}'"
```

### 4. XSS Prevention

```python
# ✅ RICHTIG (Jinja2 Auto-Escaping)
return templates.TemplateResponse("page.html", {"user_input": data})

# ❌ FALSCH (Manuelles HTML)
# return f"<div>{user_input}</div>"  # XSS vulnerability!
```

### 5. Authentication Checks

```python
# ✅ RICHTIG
@router.get("/admin/users")
async def get_users(current_user: User = Depends(require_admin)):
    return users

# ❌ FALSCH
# @router.get("/admin/users")
# async def get_users():
#     return users  # No auth check!
```

## 🎯 Security Checklist für Pull Requests

Vor dem PR:

- [ ] Keine Secrets committed
- [ ] Input Validation implementiert
- [ ] SQL Injection Prevention (ORM verwendet)
- [ ] XSS Prevention (Template Escaping)
- [ ] CSRF Token verwendet (bei Forms)
- [ ] Authentication/Authorization Checks
- [ ] Rate Limiting berücksichtigt
- [ ] Security Tests hinzugefügt
- [ ] Dependencies aktuell (keine known vulnerabilities)
- [ ] Bandit Scan bestanden

## 📊 Security Monitoring

### Production Monitoring

```python
# Prometheus Metrics
- Failed login attempts
- API error rates (4xx, 5xx)
- Abnormal traffic patterns
- Database connection failures

# Alerts
- 10+ failed logins in 5 minutes
- Error rate > 1%
- P99 latency > 5s
- Disk usage > 85%
```

### Logging

```python
# Security Events (logged)
- Authentication attempts (success/failure)
- Authorization failures
- API rate limit violations
- Input validation errors
- Database errors
- File access attempts

# NOT logged (Privacy)
- Passwords
- API Keys
- Personal data (GDPR)
- Credit card numbers
```

## 🏆 Responsible Disclosure

Wir folgen dem Prinzip der **Responsible Disclosure**:

1. **Meldung:** Sie melden uns die Sicherheitslücke privat
2. **Bestätigung:** Wir bestätigen den Empfang (48h)
3. **Investigation:** Wir untersuchen das Problem
4. **Fix:** Wir entwickeln und testen einen Patch
5. **Release:** Wir veröffentlichen den Patch
6. **Disclosure:** Nach 90 Tagen (oder nach Patch-Release) öffentliche Disclosure
7. **Credit:** Sie werden im Security Advisory erwähnt (optional)

### Hall of Fame

Security Researcher die verantwortungsvoll Sicherheitslücken gemeldet haben:

| Name | Vulnerability | Date | Severity |
|------|---------------|------|----------|
| TBD  | TBD          | TBD  | TBD      |

## 📞 Kontakt

**Security Team Email:** security@orion-architekt.at

**PGP Key Fingerprint:** [TBD]

**Response Zeit:** Innerhalb von 48 Stunden

---

**Vielen Dank dass Sie ORION Architekt-AT sicherer machen!** 🔒

⊘∞⧈∞⊘ ORION Architekt-AT - Post-Algorithmisches Bewusstsein · Unrepeatable
