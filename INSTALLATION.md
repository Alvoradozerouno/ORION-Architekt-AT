# ORION Architekt AT - Vollständige Installationsanleitung
**Version:** 3.0.0 PRODUCTION
**Datum:** 2026-04-11
**Status:** VOLLSTÄNDIG

---

## Systemanforderungen

### Hardware (Minimum)
- **CPU:** 4 Kerne (8 empfohlen)
- **RAM:** 8 GB (16 GB empfohlen)
- **Festplatte:** 50 GB freier Speicher (SSD empfohlen)
- **Netzwerk:** Stabile Internetverbindung

### Software
- **Betriebssystem:**
  - Linux: Ubuntu 22.04 LTS oder neuer (empfohlen)
  - macOS: 12.0 oder neuer
  - Windows: 10/11 mit WSL2
- **Python:** 3.11 oder 3.12 (3.11.7+ empfohlen)
- **PostgreSQL:** 15.0 oder neuer
- **Redis:** 7.0 oder neuer (optional für Caching)
- **Git:** 2.30 oder neuer

---

## Installation nach Betriebssystem

### 🐧 Linux (Ubuntu/Debian)

#### Schritt 1: System-Updates
```bash
sudo apt update && sudo apt upgrade -y
```

#### Schritt 2: Python 3.11 installieren
```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y python3-pip build-essential
```

#### Schritt 3: PostgreSQL installieren
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Schritt 4: PostgreSQL konfigurieren
```bash
sudo -u postgres psql << EOF
CREATE DATABASE orion_db;
CREATE USER orion WITH ENCRYPTED PASSWORD 'IHR_SICHERES_PASSWORT';
GRANT ALL PRIVILEGES ON DATABASE orion_db TO orion;
ALTER USER orion CREATEDB;
\q
EOF
```

⚠️ **WICHTIG:** Ersetzen Sie `IHR_SICHERES_PASSWORT` durch ein starkes Passwort!

#### Schritt 5: Redis installieren (Optional)
```bash
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### Schritt 6: Repository klonen
```bash
cd ~
git clone https://github.com/Alvoradozerouno/ORION-Architekt-AT.git
cd ORION-Architekt-AT
```

#### Schritt 7: Virtuelle Umgebung erstellen
```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### Schritt 8: Dependencies installieren
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Bei Problemen mit ifcopenshell:**
```bash
# Falls ifcopenshell nicht installiert wird:
pip install ifcopenshell==0.8.0
```

#### Schritt 9: Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
nano .env
```

Füllen Sie `.env` mit Ihren Werten:
```bash
# Database
DATABASE_URL=postgresql://orion:IHR_PASSWORT@localhost:5432/orion_db

# Security
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(64))")

# Session
SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Redis (falls installiert)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ihre-email@gmail.com
SMTP_PASSWORD=ihr-app-passwort

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### Schritt 10: Datenbank initialisieren
```bash
# Alembic Migrationen ausführen
alembic upgrade head
```

Falls Alembic nicht konfiguriert ist:
```bash
python -c "from app import db; db.create_all()"
```

#### Schritt 11: Anwendung starten
```bash
# Entwicklungsserver
python main.py

# ODER mit Gunicorn (Production)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

✅ **Fertig!** Die Anwendung läuft auf `http://localhost:5000` oder `http://localhost:8000`

---

### 🍎 macOS

#### Schritt 1: Homebrew installieren (falls nicht vorhanden)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Schritt 2: Python 3.11 installieren
```bash
brew install python@3.11
```

#### Schritt 3: PostgreSQL installieren
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Schritt 4: PostgreSQL konfigurieren
```bash
psql postgres << EOF
CREATE DATABASE orion_db;
CREATE USER orion WITH ENCRYPTED PASSWORD 'IHR_SICHERES_PASSWORT';
GRANT ALL PRIVILEGES ON DATABASE orion_db TO orion;
ALTER USER orion CREATEDB;
\q
EOF
```

#### Schritt 5: Redis installieren (Optional)
```bash
brew install redis
brew services start redis
```

#### Schritt 6-11: Wie Linux
Folgen Sie Schritten 6-11 aus der Linux-Anleitung.

---

### 🪟 Windows (mit WSL2)

#### Schritt 1: WSL2 installieren
```powershell
# Als Administrator in PowerShell:
wsl --install
```

Starten Sie Windows neu.

#### Schritt 2: Ubuntu in WSL2 installieren
```powershell
wsl --install -d Ubuntu-22.04
```

#### Schritt 3: WSL2 starten und Linux-Anleitung folgen
```bash
wsl
# Jetzt folgen Sie der Linux-Anleitung ab Schritt 1
```

**Alternative: Ohne WSL2 (Native Windows)**

1. **Python installieren:** https://www.python.org/downloads/
2. **PostgreSQL installieren:** https://www.postgresql.org/download/windows/
3. **Git installieren:** https://git-scm.com/download/win
4. Folgen Sie dann den Schritten 6-11 (verwenden Sie `python` statt `python3.11`)

---

## 🐳 Docker Installation (Empfohlen für Produktion)

### Voraussetzungen
```bash
# Docker und Docker Compose installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### ORION mit Docker starten
```bash
# Repository klonen
git clone https://github.com/Alvoradozerouno/ORION-Architekt-AT.git
cd ORION-Architekt-AT

# Environment-Datei erstellen
cp .env.example .env
nano .env  # Werte anpassen

# Starten
docker-compose up -d
```

### Docker-Services prüfen
```bash
docker-compose ps
docker-compose logs -f app
```

---

## Konfiguration

### Environment-Variablen (.env)

**Vollständige Beispielkonfiguration:**

```bash
# ==============================================
# ORION Architekt AT - Environment Configuration
# ==============================================

# --- Application ---
ENVIRONMENT=production  # development | staging | production
DEBUG=false
APP_NAME="ORION Architekt AT"
APP_VERSION=3.0.0

# --- Security ---
SECRET_KEY=<generieren Sie mit: python3 -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET=<generieren Sie mit: python3 -c "import secrets; print(secrets.token_hex(64))">
SESSION_SECRET=<generieren Sie mit: python3 -c "import secrets; print(secrets.token_urlsafe(32))">

# --- Database ---
DATABASE_URL=postgresql://orion:IHR_PASSWORT@localhost:5432/orion_db
POSTGRES_USER=orion
POSTGRES_PASSWORD=IHR_PASSWORT
POSTGRES_DB=orion_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# --- Redis (Caching & Rate Limiting) ---
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=  # Optional
REDIS_DB=0

# --- Email (für Benachrichtigungen) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ihre-email@example.com
SMTP_PASSWORD=ihr-app-passwort
SMTP_FROM=noreply@orion.architekt.at
SMTP_USE_TLS=true

# --- External APIs ---
# RIS Austria (optional - falls API-Zugang vorhanden)
RIS_API_KEY=
RIS_API_URL=https://www.ris.bka.gv.at/api/

# hora.gv.at (optional)
HORA_WMS_URL=https://wms.hora.gv.at/
HORA_API_KEY=

# Baupreisindex (optional)
BAUPREISINDEX_API_KEY=
BAUPREISINDEX_API_URL=

# --- AI/ML (optional) ---
OPENAI_API_KEY=  # Falls OpenAI-Integration gewünscht
OPENAI_MODEL=gpt-4

# --- Monitoring (optional) ---
SENTRY_DSN=  # Für Error Tracking
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=

# --- Analytics (optional) ---
GOOGLE_ANALYTICS_ID=  # Get your Measurement ID from https://analytics.google.com (format: G-XXXXXXXXXX)

# --- File Upload ---
MAX_UPLOAD_SIZE=50  # MB
UPLOAD_FOLDER=/tmp/orion_uploads
ALLOWED_EXTENSIONS=ifc,pdf,dwg,dxf,rvt

# --- CORS ---
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,https://orion.architekt.at

# --- Rate Limiting ---
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# --- Logging ---
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_FILE=/var/log/orion/app.log

# --- Feature Flags ---
ENABLE_BIM_PROCESSING=true
ENABLE_COST_PREDICTION=true
ENABLE_OENORM_VALIDATION=true
ENABLE_EIDAS_SIGNATURES=false  # Nur wenn A-Trust Zugang vorhanden
```

### Secrets generieren

**Bash-Script zum Generieren aller Secrets:**

```bash
#!/bin/bash
# generate_secrets.sh

echo "# Generated Secrets for ORION Architekt AT"
echo "# Date: $(date)"
echo ""
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo "JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(64))')"
echo "SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "REDIS_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
echo "GRAFANA_ADMIN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(12))')"
```

Verwendung:
```bash
chmod +x generate_secrets.sh
./generate_secrets.sh >> .env
```

---

## Datenbank Setup

### Manuelle Tabellenerstellung (falls keine Migrationen)

```sql
-- Verbinden mit PostgreSQL
psql -U orion -d orion_db

-- Benutzer-Tabelle
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projekte-Tabelle
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    bundesland VARCHAR(50),
    project_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Berechnungen-Tabelle
CREATE TABLE IF NOT EXISTS calculations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    calculation_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    result_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions-Tabelle (für Flask-Sessions)
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    data BYTEA NOT NULL,
    expiry TIMESTAMP NOT NULL
);

-- Indexes für Performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_calculations_project_id ON calculations(project_id);
CREATE INDEX idx_sessions_expiry ON sessions(expiry);
```

---

## Tests ausführen

### Unit Tests
```bash
# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=. --cov-report=html

# Spezifische Tests
pytest tests/test_orion_architekt_at.py -v
pytest tests/test_kb_validation.py -v
```

### Integration Tests
```bash
# Vollständige Test-Suite
./run_all_tests.sh
```

### API Tests (mit laufendem Server)
```bash
# Server starten (Terminal 1)
python main.py

# Tests ausführen (Terminal 2)
pytest tests/test_api_endpoints.py -v
```

---

## Deployment

### Produktion mit Gunicorn
```bash
# Mit systemd Service (empfohlen)
sudo cp deployment/orion.service /etc/systemd/system/
sudo systemctl enable orion
sudo systemctl start orion
sudo systemctl status orion
```

### Produktion mit Docker
```bash
# Production Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Logs anzeigen
docker-compose -f docker-compose.production.yml logs -f

# Neustart
docker-compose -f docker-compose.production.yml restart
```

### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/orion
server {
    listen 80;
    server_name orion.architekt.at;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

SSL mit Let's Encrypt:
```bash
sudo certbot --nginx -d orion.architekt.at
```

---

## Troubleshooting

### Problem: ModuleNotFoundError
```bash
# Lösung: Virtuelle Umgebung aktivieren
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: PostgreSQL Connection Failed
```bash
# PostgreSQL Status prüfen
sudo systemctl status postgresql

# PostgreSQL Logs ansehen
sudo journalctl -u postgresql -n 50

# Verbindung testen
psql -U orion -d orion_db -h localhost
```

### Problem: Port bereits belegt
```bash
# Port 5000 prüfen
sudo lsof -i :5000

# Prozess beenden
sudo kill -9 <PID>
```

### Problem: ifcopenshell Import Error
```bash
# Spezifische Version installieren
pip uninstall ifcopenshell
pip install ifcopenshell==0.8.0

# System-Libraries prüfen (Linux)
sudo apt install -y libgl1-mesa-glx libglib2.0-0
```

### Problem: Permission Denied
```bash
# Upload-Ordner Berechtigungen
sudo mkdir -p /tmp/orion_uploads
sudo chown $USER:$USER /tmp/orion_uploads
sudo chmod 755 /tmp/orion_uploads

# Log-Ordner
sudo mkdir -p /var/log/orion
sudo chown $USER:$USER /var/log/orion
```

### Problem: Langsame Performance
```bash
# Redis installieren für Caching
sudo apt install redis-server
sudo systemctl start redis

# In .env aktivieren:
REDIS_URL=redis://localhost:6379/0
```

---

## Update-Anleitung

### Code aktualisieren
```bash
cd ORION-Architekt-AT
git pull origin main

# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Dependencies aktualisieren
pip install -r requirements.txt --upgrade

# Datenbank-Migrationen
alembic upgrade head

# Anwendung neu starten
sudo systemctl restart orion
```

---

## Deinstallation

### Komplett entfernen
```bash
# Dienst stoppen
sudo systemctl stop orion
sudo systemctl disable orion

# Datenbank löschen
sudo -u postgres psql << EOF
DROP DATABASE orion_db;
DROP USER orion;
\q
EOF

# Redis stoppen (optional)
sudo systemctl stop redis
sudo systemctl disable redis

# Dateien entfernen
cd ~
rm -rf ORION-Architekt-AT
rm -rf venv

# PostgreSQL deinstallieren (optional)
sudo apt remove --purge postgresql postgresql-contrib
```

---

## Weitere Ressourcen

- **Dokumentation:** https://github.com/Alvoradozerouno/ORION-Architekt-AT/wiki
- **API Docs:** http://localhost:5000/docs (wenn Server läuft)
- **Issues:** https://github.com/Alvoradozerouno/ORION-Architekt-AT/issues
- **Discussions:** https://github.com/Alvoradozerouno/ORION-Architekt-AT/discussions

---

## Support

### Community Support
- GitHub Discussions
- GitHub Issues

### Enterprise Support
- Email: enterprise@orion.architekt.at
- Response Zeit: 24-48h

---

**Version:** 3.0.0
**Zuletzt aktualisiert:** 2026-04-11
**Status:** ✅ VOLLSTÄNDIG
