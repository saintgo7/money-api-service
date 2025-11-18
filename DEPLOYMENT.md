# Money API Service - Deployment Guide

Complete guide for deploying Money API Service to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Database Migrations](#database-migrations)
8. [Environment Variables](#environment-variables)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for K8s deployment)
- kubectl
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Cloud Provider Accounts (Optional)
- AWS/GCP/Azure for cloud deployment
- Domain name for SSL
- Stripe account for payments

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-org/money-api-service.git
cd money-api-service
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-graphql.txt -r requirements-dev.txt
```

### 4. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- GraphQL: `http://localhost:8000/graphql`

---

## Docker Deployment

### Production with Docker Compose

#### 1. Configure Environment

```bash
cp .env.production .env
# Edit .env with production values
```

**Critical Settings:**
```env
SECRET_KEY=<generate-secure-random-key>
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@postgres:5432/money_api
REDIS_URL=redis://:PASSWORD@redis:6379/0

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

#### 2. Generate Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

#### 3. Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Verify Deployment

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f api

# Test health endpoint
curl http://localhost:8000/health
```

#### 5. Run Migrations

```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

---

## Kubernetes Deployment

### 1. Prepare Cluster

```bash
# Create namespace
kubectl create namespace money-api

# Set context
kubectl config set-context --current --namespace=money-api
```

### 2. Create Secrets

```bash
# Create secret from .env
kubectl create secret generic money-api-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://..." \
  --from-literal=REDIS_URL="redis://..." \
  --from-literal=SECRET_KEY="..." \
  --from-literal=ANTHROPIC_API_KEY="..." \
  --from-literal=OPENAI_API_KEY="..." \
  --from-literal=STRIPE_SECRET_KEY="..."
```

### 3. Deploy Application

```bash
# Apply all manifests
kubectl apply -f kubernetes/deployment.yaml

# Verify deployment
kubectl get pods
kubectl get svc
kubectl get ingress
```

### 4. Database Setup

```bash
# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=money-api --timeout=300s

# Run migrations
kubectl exec -it deployment/money-api-deployment -- alembic upgrade head
```

### 5. Access Application

```bash
# Get external IP
kubectl get svc money-api-service

# Port forward for testing
kubectl port-forward svc/money-api-service 8000:80

# Test
curl http://localhost:8000/health
```

---

## Monitoring Setup

### Prometheus & Grafana

#### 1. Access Grafana

```bash
# Docker Compose
http://localhost:3001
# Default credentials: admin / (from GRAFANA_PASSWORD env)

# Kubernetes
kubectl port-forward svc/grafana 3000:3000
http://localhost:3000
```

#### 2. Import Dashboards

1. Login to Grafana
2. Navigate to Dashboards → Import
3. Upload `grafana/dashboards/api-overview.json`

#### 3. Configure Alerts

Edit `prometheus/alerts/api-alerts.yml` and apply:

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml restart prometheus

# Kubernetes
kubectl apply -f kubernetes/prometheus-configmap.yaml
kubectl rollout restart deployment/prometheus
```

### Sentry Integration

```bash
# Add Sentry DSN to environment
SENTRY_DSN=https://...@sentry.io/...

# Restart application
docker-compose -f docker-compose.prod.yml restart api
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

#### 1. Install Certbot

```bash
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d api.moneyapi.example.com \
  --email your@email.com \
  --agree-tos
```

#### 2. Update Nginx Configuration

```nginx
# nginx/nginx.conf
ssl_certificate /etc/letsencrypt/live/api.moneyapi.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/api.moneyapi.example.com/privkey.pem;
```

#### 3. Setup Auto-Renewal

```bash
# Crontab
0 0 * * * docker run --rm -v /etc/letsencrypt:/etc/letsencrypt certbot/certbot renew
```

### Kubernetes with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your@email.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Database Migrations

### Create Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Add new feature"

# Review generated migration in alembic/versions/
```

### Apply Migrations

```bash
# Development
alembic upgrade head

# Docker
docker-compose exec api alembic upgrade head

# Kubernetes
kubectl exec -it deployment/money-api-deployment -- alembic upgrade head
```

### Rollback

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>
```

---

## Environment Variables

### Required Variables

```env
# Application
APP_NAME=Money API Service
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=<32-byte-random-string>

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://:pass@host:6379/0
CLICKHOUSE_HOST=clickhouse-host
CLICKHOUSE_PORT=9000

# AI Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REPLICATE_API_KEY=r8_...
ELEVENLABS_API_KEY=...

# Payments
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=...
FROM_EMAIL=noreply@moneyapi.example.com

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
PROMETHEUS_PORT=9090

# Security
CORS_ORIGINS=https://dashboard.example.com,https://api.example.com
ALLOWED_HOSTS=api.example.com
ENABLE_HTTPS=true
```

---

## Scaling

### Horizontal Scaling (Kubernetes)

```bash
# Manual scaling
kubectl scale deployment money-api-deployment --replicas=5

# Auto-scaling (already configured in deployment.yaml)
# HPA scales from 3 to 10 replicas based on CPU/Memory
kubectl get hpa
```

### Database Scaling

```bash
# PostgreSQL read replicas
# Update DATABASE_URL to use read replica for read operations

# Redis cluster
# Configure Redis Sentinel or Cluster mode
```

### Load Testing

```bash
# Install k6
# Load test endpoints
k6 run - <<EOF
import http from 'k6/http';
export let options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
};
export default function () {
  http.get('https://api.moneyapi.example.com/health');
}
EOF
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
docker-compose exec postgres psql -U postgres -d money_api
```

#### 2. Redis Connection Failed

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Check password
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

#### 3. High Memory Usage

```bash
# Check container stats
docker stats

# Kubernetes
kubectl top pods

# Restart services
docker-compose restart api
# or
kubectl rollout restart deployment/money-api-deployment
```

#### 4. Slow API Response

```bash
# Check logs for slow queries
docker-compose logs api | grep "Slow query"

# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=http_request_duration_seconds

# Check database connections
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Logs

```bash
# Application logs
docker-compose logs -f api

# All services
docker-compose logs -f

# Kubernetes
kubectl logs -f deployment/money-api-deployment
kubectl logs -f -l app=money-api --all-containers=true
```

### Health Checks

```bash
# API health
curl https://api.moneyapi.example.com/health

# Metrics
curl https://api.moneyapi.example.com/metrics

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Database migrations applied
- [ ] Monitoring configured (Prometheus + Grafana)
- [ ] Error tracking enabled (Sentry)
- [ ] Backups configured
- [ ] Log aggregation setup
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Stripe webhooks configured
- [ ] Email service working
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] CI/CD pipeline configured
- [ ] Documentation updated

---

## Support

- **Documentation**: https://docs.moneyapi.example.com
- **Email**: devops@moneyapi.example.com
- **Slack**: #money-api-support
- **GitHub Issues**: https://github.com/your-org/money-api-service/issues
