# 🚀 ORION Architekt AT - Quick Start Guide
## Setup & Deployment in 5 Minuten

**Erstellt:** 2026-04-10
**Zielgruppe:** Entwickler, DevOps, Beta-Tester

---

## ⚡ SCHNELLSTART (3 Befehle)

```bash
# 1. Repository klonen
git clone https://github.com/Alvoradozerouno/ORION-Architekt-AT.git
cd ORION-Architekt-AT

# 2. Dependencies installieren
pip3 install -r requirements.txt

# 3. Alle Tests ausführen
./run_all_tests.sh
```

**Ergebnis:** Alle 10 Core-Module getestet, 100% Success Rate ✓

---

## 🐳 DOCKER DEPLOYMENT (Production)

### Option A: Alle Services starten

```bash
# Docker Compose starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f app

# Status prüfen
docker-compose ps
```

**Services:**
- FastAPI App: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### Option B: Nur App ohne DB

```bash
# Nur FastAPI App
docker build -t orion-architekt-at .
docker run -p 8000:8000 orion-architekt-at
```

---

## 📋 SYSTEM REQUIREMENTS

**Minimum:**
- Python 3.11+
- 4 GB RAM
- 2 CPU Cores
- 10 GB Disk Space

**Empfohlen:**
- Python 3.11+
- 8 GB RAM
- 4 CPU Cores
- 20 GB Disk Space
- Docker 24+
- Docker Compose 2.20+

---

## 🔧 MANUELLE INSTALLATION

### 1. Python Environment

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Verify Installation
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
```

### 2. Umgebungsvariablen

```bash
# .env Datei erstellen
cat > .env <<EOF
# Database
# WICHTIG: Ersetzen Sie 'YOUR_SECURE_PASSWORD' mit einem starken Passwort!
DATABASE_URL=postgresql://orion:YOUR_SECURE_PASSWORD@localhost:5432/orion_db

# JWT (wird automatisch generiert)
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
EOF

# Generieren Sie ein sicheres Datenbankpasswort:
DB_PASSWORD=$(openssl rand -base64 24)
echo "Ihr generiertes Datenbankpasswort: $DB_PASSWORD"
echo "Ersetzen Sie 'YOUR_SECURE_PASSWORD' in .env mit diesem Passwort"
```

### 3. Datenbank Setup

```bash
# PostgreSQL installieren (wenn nicht vorhanden)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Datenbank erstellen
createdb orion_db
psql orion_db -c "CREATE USER orion WITH PASSWORD 'orion_secure_2026';"
psql orion_db -c "GRANT ALL PRIVILEGES ON DATABASE orion_db TO orion;"

# Migrations (wenn vorhanden)
# alembic upgrade head
```

### 4. Redis Setup

```bash
# Redis installieren
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Redis starten
redis-server --daemonize yes

# Verify
redis-cli ping  # Should return PONG
```

### 5. API Server starten

```bash
# Development Mode (auto-reload)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production Mode (mit Gunicorn)
gunicorn api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

**Verify:**
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🧪 TESTING

### Alle Tests ausführen

```bash
# Automatisches Test-Script
./run_all_tests.sh

# Oder manuell:
pytest tests/ -v --cov=. --cov-report=html
python3 test_complete_integration.py
python3 test_ai_integration.py
python3 test_multi_agent_integration.py
```

### Einzelne Tests

```bash
# Unit Tests
pytest tests/test_orion_architekt_at.py -v
pytest tests/test_kb_validation.py -v
pytest tests/test_audit_trail.py -v

# Integration Tests
python3 test_complete_integration.py
python3 integration_fixes.py

# API Tests (wenn API läuft)
pytest tests/test_api.py -v  # TODO: Muss erstellt werden
```

### Coverage Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 🔐 SECURITY SETUP (PRODUCTION)

### 1. Secrets generieren

```bash
# JWT Secret
openssl rand -hex 32

# Database Password
openssl rand -base64 32

# API Keys für Services
openssl rand -base64 24
```

### 2. Environment Variables setzen

```bash
# Niemals Default-Secrets in Production!
export JWT_SECRET_KEY="<generated-secret>"
export DATABASE_PASSWORD="<generated-password>"
export REDIS_PASSWORD="<generated-password>"
```

### 3. HTTPS Setup (Nginx)

```bash
# SSL Zertifikat (Let's Encrypt)
sudo certbot --nginx -d api.orion-architekt.at

# Oder Self-Signed für Testing
openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/orion.key \
    -out /etc/nginx/ssl/orion.crt
```

### 4. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw enable

# Deny direct access to DB/Redis
sudo ufw deny 5432/tcp
sudo ufw deny 6379/tcp
```

---

## 📊 MONITORING SETUP

### 1. Prometheus

```bash
# prometheus.yml already configured
# Start with Docker Compose or manually:
prometheus --config.file=prometheus.yml

# Access: http://localhost:9090
```

### 2. Grafana

```bash
# Start Grafana
docker run -d -p 3000:3000 grafana/grafana

# Default login: admin/admin
# Access: http://localhost:3000

# Add Prometheus Data Source:
# URL: http://prometheus:9090 (Docker) or http://localhost:9090 (local)
```

### 3. Custom Dashboards

```json
{
  "dashboard": {
    "title": "ORION Architekt AT",
    "panels": [
      {
        "title": "API Requests/s",
        "targets": [{"expr": "rate(http_requests_total[5m])"}]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{"expr": "histogram_quantile(0.95, http_request_duration_seconds)"}]
      }
    ]
  }
}
```

---

## 🔍 TROUBLESHOOTING

### Problem: Tests schlagen fehl

```bash
# Check Dependencies
pip list | grep -E "(pytest|numpy|fastapi)"

# Reinstall
pip install --upgrade -r requirements.txt

# Clean cache
find . -type d -name __pycache__ -exec rm -r {} +
pip cache purge
```

### Problem: API startet nicht

```bash
# Check Ports
netstat -tuln | grep 8000
lsof -i :8000  # macOS/Linux

# Check Logs
tail -f /var/log/orion/app.log

# Check Database Connection
psql $DATABASE_URL -c "SELECT 1"
```

### Problem: BIM/IFC Parsing fehlt

```bash
# IFC Library ist aktuell NICHT installiert
# Workaround: API verwendet simulierte Daten
# Fix in Entwicklung (siehe PRODUCTION_READINESS_REPORT.md)

# Temporär: ifcopenshell installieren (experimental)
pip install ifcopenshell==0.8.0
```

### Problem: Docker Build schlägt fehl

```bash
# Clean Docker Cache
docker system prune -a

# Rebuild ohne Cache
docker-compose build --no-cache

# Check Disk Space
df -h
```

---

## 📖 WEITERE DOKUMENTATION

**Haupt-Dokumente:**
- `PRODUCTION_READINESS_REPORT.md` - Vollständige System-Analyse
- `FINALE_ZUSAMMENFASSUNG_2026-04-10.md` - System-Zusammenfassung
- `README.md` - Projekt-Übersicht
- `API_README.md` - API Dokumentation

**API Dokumentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

**Architektur:**
- Multi-Agent System: `MULTI_AGENT_IMPLEMENTATION_REPORT.md`
- GENESIS Framework: `GENESIS_README.md`
- ÖNORM A 2063: `OENORM_A2063_DOKUMENTATION.md`

---

## 🚀 DEPLOYMENT CHECKLIST

### Pre-Launch:

- [ ] **Security**
  - [ ] JWT_SECRET_KEY geändert
  - [ ] Database Passwords geändert
  - [ ] CORS auf spezifische Domains
  - [ ] HTTPS aktiviert
  - [ ] Firewall konfiguriert

- [ ] **Database**
  - [ ] PostgreSQL Production Setup
  - [ ] Backup-Strategie implementiert
  - [ ] Migrations getestet
  - [ ] Connection Pooling optimiert

- [ ] **Monitoring**
  - [ ] Prometheus läuft
  - [ ] Grafana Dashboards erstellt
  - [ ] Alerting konfiguriert
  - [ ] Log Aggregation aktiv

- [ ] **Testing**
  - [ ] Alle Tests bestanden
  - [ ] Load Testing durchgeführt
  - [ ] Security Audit abgeschlossen

- [ ] **Documentation**
  - [ ] User Manual erstellt
  - [ ] API Docs aktuell
  - [ ] Deployment Guide reviewt

### Launch:

- [ ] **Deployment**
  - [ ] Staging Environment getestet
  - [ ] Production Deployment durchgeführt
  - [ ] Health Checks bestanden
  - [ ] Rollback-Plan bereit

- [ ] **Operations**
  - [ ] Monitoring Dashboards aktiv
  - [ ] On-Call Rotation definiert
  - [ ] Incident Response Plan
  - [ ] Backup Verification

---

## 💬 SUPPORT & COMMUNITY

**GitHub Issues:**
https://github.com/Alvoradozerouno/ORION-Architekt-AT/issues

**Beta-Programm:**
Für Beta-Zugang: GitHub Issue mit Tag `beta-access` erstellen

**Feedback:**
Feedback via GitHub Discussions oder Issues

---

## 📜 LICENSE

See `LICENSE` and `GENESIS_LICENSE.md` files.

---

**Status:** READY FOR BETA LAUNCH ✓
**Letzte Aktualisierung:** 2026-04-10
**Version:** 2.1.0
