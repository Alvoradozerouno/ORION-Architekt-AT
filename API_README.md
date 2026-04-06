# ORION Architekt-AT API

Production-ready REST API for Austrian building regulations, compliance checking, and architectural calculations.

## 🚀 Features

### Core Functionality
- **30+ Building Calculations**: U-Wert, Stellplätze, Flächenberechnung, Schallschutz, Heizlast, etc.
- **Complete OIB-RL 1-6 Coverage**: Automated compliance checking for all Austrian building directives
- **9 Bundesländer Support**: Specific regulations for Wien, Tirol, Salzburg, Vorarlberg, Kärnten, Steiermark, Oberösterreich, Niederösterreich, Burgenland
- **ÖNORM Standards**: Implementation of key Austrian standards (B 1800, B 1600, B 8115-2, EN ISO 6946, etc.)
- **Knowledge Base Validation**: Automatic verification of data sources (RIS Austria, OIB, ÖNORM, hora.gv.at)

### 🎯 Unique Features (Competitive Advantages)

#### 1. AI-Powered Building Optimization
- Material recommendations optimized for cost & Austrian compliance
- Energy efficiency improvements with ML-based predictions
- Cost prediction using historical data & bundesland-specific pricing
- Market insights and trends analysis
- Bundesland-specific optimizations

#### 2. BIM Integration Layer
- IFC file parsing and validation (IFC2x3, IFC4, IFC4.3)
- Automatic compliance checking from BIM models
- U-Wert calculation directly from BIM materials
- Clash detection with Austrian regulations
- Material extraction with ÖNORM validation
- Geometry analysis for Barrierefreiheit, Fluchtwege, Stellplätze

#### 3. Real-time Multi-user Collaboration
- WebSocket-based live updates
- Project sharing with role-based permissions (architect, engineer, client, viewer)
- Comment system with threading
- Activity feed tracking all changes
- Version control with restore capability
- Online user presence indicators

## 📦 Installation

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/Alvoradozerouno/ORION-Architekt-AT.git
cd ORION-Architekt-AT

# Start all services
docker-compose up -d

# API available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/orion"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/orion

# Redis (for caching and rate limiting)
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,https://orion-architekt.at
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

```bash
# Register new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"demo12345"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo12345"}'

# Use token in requests
curl -X GET http://localhost:8000/api/v1/calculations/materialdatenbank \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Example Requests

#### Calculate U-Wert
```bash
curl -X POST http://localhost:8000/api/v1/calculations/uwert \
  -H "Content-Type: application/json" \
  -d '{
    "schichten": [
      {"material": "Ziegel", "dicke_mm": 250, "lambda_wert": 0.65},
      {"material": "EPS Dämmung", "dicke_mm": 200, "lambda_wert": 0.035}
    ]
  }'
```

#### Check OIB-RL Compliance
```bash
curl -X POST http://localhost:8000/api/v1/compliance/oib-rl-check \
  -H "Content-Type: application/json" \
  -d '{
    "bundesland": "wien",
    "building_type": "mehrfamilienhaus",
    "bgf_m2": 1200,
    "geschosse": 4,
    "wohnungen": 12
  }'
```

#### Upload IFC File for BIM Analysis
```bash
curl -X POST http://localhost:8000/api/v1/bim/upload-ifc \
  -F "file=@building.ifc" \
  -F "bundesland=wien" \
  -F "building_type=mehrfamilienhaus"
```

#### AI Building Optimization
```bash
curl -X POST http://localhost:8000/api/v1/ai/optimize-building \
  -H "Content-Type: application/json" \
  -d '{
    "bundesland": "tirol",
    "gebaudetyp": "mehrfamilienhaus",
    "bgf_m2": 500,
    "geschosse": 3,
    "wohnungen": 6,
    "budget_euro": 800000,
    "energieziel": "A+"
  }'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                  │
│                  Reverse Proxy                      │
└───────────┬─────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────┐
│              FastAPI Application                     │
│                  (Port 8000)                        │
├─────────────────────────────────────────────────────┤
│  Routers:                                           │
│  - Calculations  - Compliance  - Validation         │
│  - Bundesland    - Reports     - AI                 │
│  - BIM           - Collaboration                    │
├─────────────────────────────────────────────────────┤
│  Middleware:                                        │
│  - Authentication  - Rate Limiting                  │
│  - Logging         - CORS                           │
└────┬──────────────────────────┬─────────────────────┘
     │                          │
┌────▼──────────────┐   ┌───────▼──────────────┐
│   PostgreSQL      │   │       Redis          │
│   (Port 5432)     │   │    (Port 6379)       │
│   - Users         │   │    - Cache           │
│   - Projects      │   │    - Rate Limits     │
│   - Comments      │   │    - Sessions        │
└───────────────────┘   └──────────────────────┘
```

## 📊 Monitoring

### Prometheus Metrics
- Request rate and latency
- Error rates
- Database connections
- Redis memory usage
- WebSocket connections

Access: http://localhost:9090

### Grafana Dashboards
- API performance overview
- Endpoint analytics
- System health
- User activity

Access: http://localhost:3000 (admin/admin)

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Tiered rate limits (100/hr anonymous, 1k/hr authenticated, 10k/hr premium)
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS**: Configurable cross-origin resource sharing
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_calculations.py

# Run parallel tests
pytest -n auto
```

## 📈 Performance

- **Multi-stage Docker build**: Optimized image size
- **Connection pooling**: Efficient database connections
- **Redis caching**: Fast response times for repeated queries
- **Compression**: Gzip middleware for reduced bandwidth
- **Async operations**: Non-blocking I/O for high concurrency

## 🌍 Bundesländer Support

| Bundesland        | Stellplatz Factor | Aufzug ab Geschoss | Special Regulations |
|-------------------|-------------------|-------------------|---------------------|
| Wien              | 1.2               | 4                 | Dachgeschoßausbau   |
| Tirol             | 1.5               | 4                 | Lawinenschutz       |
| Salzburg          | 1.3               | 4                 | Altstadtschutz      |
| Vorarlberg        | 1.4               | 4                 | Energiestandard+    |
| Kärnten           | 1.2               | 4                 | -                   |
| Steiermark        | 1.3               | 4                 | -                   |
| Oberösterreich    | 1.3               | 4                 | -                   |
| Niederösterreich  | 1.2               | 4                 | -                   |
| Burgenland        | 1.0               | 4                 | -                   |

## 🔄 Development

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Format code
black .
isort .

# Lint
flake8 .
pylint api/
mypy api/

# Security scan
bandit -r api/
safety check
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

- Documentation: https://github.com/Alvoradozerouno/ORION-Architekt-AT
- Issues: https://github.com/Alvoradozerouno/ORION-Architekt-AT/issues
- Email: support@orion-architekt.at

---

**Version**: 3.0.0
**Last Updated**: 2026-04-06
**Status**: Production Ready ✅
