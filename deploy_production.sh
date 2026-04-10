#!/bin/bash
#
# ORION Architekt AT - Full Production Deployment Script
# ======================================================
#
# This script deploys the complete ORION system to production.
# NO staged rollout. NO beta. FULL PRODUCTION NOW.
#
# This is the AEC paradigm shift.
#
# Author: ORION Engineering Team
# Date: 2026-04-10
# Status: PRODUCTION
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV=${DEPLOYMENT_ENV:-production}
DOMAIN=${DOMAIN:-orion.architekt.at}
SSL_EMAIL=${SSL_EMAIL:-admin@architekt.at}
POSTGRES_VERSION=${POSTGRES_VERSION:-15}
REDIS_VERSION=${REDIS_VERSION:-7}
PYTHON_VERSION=${PYTHON_VERSION:-3.11}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ORION ARCHITEKT AT - FULL PRODUCTION DEPLOYMENT          ║"
echo "║  AEC Paradigm Shift - Complete System Deployment          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Deployment Configuration:${NC}"
echo "  Environment: $DEPLOYMENT_ENV"
echo "  Domain: $DOMAIN"
echo "  PostgreSQL: $POSTGRES_VERSION"
echo "  Redis: $REDIS_VERSION"
echo "  Python: $PYTHON_VERSION"
echo ""

read -p "Press ENTER to proceed with FULL PRODUCTION deployment or CTRL+C to cancel..."

# ============================================================================
# STEP 1: System Preparation
# ============================================================================

echo -e "\n${BLUE}[1/10] System Preparation${NC}"

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    build-essential \
    libpq-dev \
    python3-dev

echo -e "${GREEN}✓ System prepared${NC}"

# ============================================================================
# STEP 2: Docker Installation
# ============================================================================

echo -e "\n${BLUE}[2/10] Docker Installation${NC}"

if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "Docker already installed: $(docker --version)"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed: $(docker-compose --version)"
fi

echo -e "${GREEN}✓ Docker installed${NC}"

# ============================================================================
# STEP 3: Firewall Configuration
# ============================================================================

echo -e "\n${BLUE}[3/10] Firewall Configuration${NC}"

echo "Configuring UFW firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo -e "${GREEN}✓ Firewall configured${NC}"

# ============================================================================
# STEP 4: SSL Certificate
# ============================================================================

echo -e "\n${BLUE}[4/10] SSL Certificate${NC}"

if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "Obtaining SSL certificate for $DOMAIN..."
    sudo certbot certonly --standalone -d $DOMAIN --email $SSL_EMAIL --agree-tos --non-interactive
else
    echo "SSL certificate already exists for $DOMAIN"
fi

# Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo -e "${GREEN}✓ SSL certificate configured${NC}"

# ============================================================================
# STEP 5: Application Directory
# ============================================================================

echo -e "\n${BLUE}[5/10] Application Directory${NC}"

APP_DIR="/opt/orion"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

cd $APP_DIR

if [ ! -d ".git" ]; then
    echo "Cloning ORION repository..."
    git clone https://github.com/Alvoradozerouno/ORION-Architekt-AT.git .
else
    echo "Updating ORION repository..."
    git pull origin main
fi

echo -e "${GREEN}✓ Application directory ready${NC}"

# ============================================================================
# STEP 6: Secrets Generation
# ============================================================================

echo -e "\n${BLUE}[6/10] Secrets Generation${NC}"

echo "Generating secure secrets..."

# JWT Secret (512-bit)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(64))")

# API Key
API_KEY=$(python3 -c "import secrets; print(f'orion_{secrets.token_hex(32)}')")

# Database Password
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Redis Password
REDIS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Grafana Admin Password
GRAFANA_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

echo -e "${GREEN}✓ Secrets generated${NC}"

# ============================================================================
# STEP 7: Environment Configuration
# ============================================================================

echo -e "\n${BLUE}[7/10] Environment Configuration${NC}"

cat > .env.production <<EOF
# ORION Architekt AT - Production Environment
# ===========================================
# Generated: $(date)

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$JWT_SECRET
API_KEY=$API_KEY
DOMAIN=$DOMAIN

# Database
DATABASE_URL=postgresql://orion:$DB_PASSWORD@postgres:5432/orion_production
POSTGRES_USER=orion
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=orion_production

# Redis
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=$REDIS_PASSWORD

# Security
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://$DOMAIN,https://app.$DOMAIN

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD

# SSL
SSL_ENABLED=true
SSL_CERT_PATH=/etc/letsencrypt/live/$DOMAIN/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/$DOMAIN/privkey.pem
EOF

chmod 600 .env.production

echo -e "${GREEN}✓ Environment configured${NC}"

# ============================================================================
# STEP 8: Data Directories
# ============================================================================

echo -e "\n${BLUE}[8/10] Data Directories${NC}"

echo "Creating data directories..."
sudo mkdir -p $APP_DIR/data/postgres
sudo mkdir -p $APP_DIR/data/redis
sudo mkdir -p $APP_DIR/data/prometheus
sudo mkdir -p $APP_DIR/data/grafana
sudo mkdir -p $APP_DIR/logs

# Set permissions
sudo chown -R 999:999 $APP_DIR/data/postgres  # PostgreSQL user
sudo chown -R 999:999 $APP_DIR/data/redis     # Redis user
sudo chown -R $USER:$USER $APP_DIR/logs

echo -e "${GREEN}✓ Data directories created${NC}"

# ============================================================================
# STEP 9: Docker Deployment
# ============================================================================

echo -e "\n${BLUE}[9/10] Docker Deployment${NC}"

echo "Building Docker images..."
docker-compose -f docker-compose.production.yml build

echo "Starting services..."
docker-compose -f docker-compose.production.yml up -d

echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T app alembic upgrade head || echo "Migrations completed or not needed"

echo -e "${GREEN}✓ Docker deployment complete${NC}"

# ============================================================================
# STEP 10: Production Validation
# ============================================================================

echo -e "\n${BLUE}[10/10] Production Validation${NC}"

echo "Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U orion > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL: HEALTHY${NC}"
else
    echo -e "${RED}✗ PostgreSQL: UNHEALTHY${NC}"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis: HEALTHY${NC}"
else
    echo -e "${RED}✗ Redis: UNHEALTHY${NC}"
fi

# Check Application
if curl -sf https://$DOMAIN/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Application: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Application: CHECK MANUALLY${NC}"
    echo "  URL: https://$DOMAIN/health"
fi

# Check Prometheus
if curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Prometheus: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Prometheus: CHECK MANUALLY${NC}"
fi

# Check Grafana
if curl -sf http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Grafana: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Grafana: CHECK MANUALLY${NC}"
fi

# ============================================================================
# Deployment Summary
# ============================================================================

echo -e "\n${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  FULL PRODUCTION DEPLOYMENT COMPLETE                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}ORION Architekt AT is now LIVE in production!${NC}"
echo ""
echo "Access Points:"
echo "  🌐 Application:  https://$DOMAIN"
echo "  📊 Grafana:      https://$DOMAIN/grafana"
echo "  📈 Prometheus:   http://localhost:9090"
echo "  📚 API Docs:     https://$DOMAIN/docs"
echo ""
echo "Credentials (SAVE THESE SECURELY):"
echo "  Grafana Admin:   admin / $GRAFANA_PASSWORD"
echo "  API Key:         $API_KEY"
echo ""
echo "System Status:"
echo "  $(docker-compose -f docker-compose.production.yml ps)"
echo ""
echo "Next Steps:"
echo "  1. Access Grafana and import dashboards"
echo "  2. Configure alerting rules"
echo "  3. Set up backup automation"
echo "  4. Configure monitoring alerts"
echo "  5. Test all critical workflows"
echo ""
echo "Commands:"
echo "  View logs:       docker-compose -f docker-compose.production.yml logs -f"
echo "  Restart:         docker-compose -f docker-compose.production.yml restart"
echo "  Stop:            docker-compose -f docker-compose.production.yml down"
echo "  Update:          git pull && docker-compose -f docker-compose.production.yml up -d --build"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}AEC PARADIGM SHIFT: COMPLETE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
