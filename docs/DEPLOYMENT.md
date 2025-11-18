# Deployment Guide

## Prerequisites

- Linux server (Ubuntu 22.04 LTS recommended)
- Docker & Docker Compose installed
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Create application user
sudo useradd -m -s /bin/bash moneyapi
sudo usermod -aG docker moneyapi
```

### 2. Clone and Configure

```bash
# Switch to app user
sudo su - moneyapi

# Clone repository
git clone https://github.com/yourusername/money-api-service.git
cd money-api-service

# Configure environment
cp .env.example .env
nano .env  # Edit with production values
```

### 3. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot -y

# Get certificate
sudo certbot certonly --standalone -d api.yourdomain.com
```

### 4. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/moneyapi`:

```nginx
upstream api_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/moneyapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Deploy Application

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

### 6. Monitoring Setup

```bash
# Access Prometheus
http://your-server:9090

# Access Grafana
http://your-server:3001

# Import dashboards
# - FastAPI metrics
# - PostgreSQL metrics
# - Redis metrics
```

## Kubernetes Deployment

### 1. Create Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: money-api
```

### 2. Deploy PostgreSQL

```yaml
# postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: money-api
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: money_api
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

### 3. Deploy Application

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: money-api
  namespace: money-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: money-api
  template:
    metadata:
      labels:
        app: money-api
    spec:
      containers:
      - name: api
        image: your-registry/money-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: database-url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4. Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: money-api-ingress
  namespace: money-api
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: money-api
            port:
              number: 8000
```

## Database Backups

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

# Create backup
docker-compose exec -T postgres pg_dump -U postgres money_api > \
  $BACKUP_DIR/backup_$DATE.sql

# Compress
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz \
  s3://your-bucket/backups/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Scaling

### Horizontal Scaling

```bash
# Scale API servers
docker-compose up -d --scale api=5

# Or with Kubernetes
kubectl scale deployment money-api --replicas=5 -n money-api
```

### Database Connection Pooling

Update `src/core/database.py`:

```python
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

## Monitoring & Alerts

### Prometheus Alerts

```yaml
# alerts.yml
groups:
- name: api_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: HighLatency
    expr: http_request_duration_seconds{quantile="0.99"} > 1
    for: 5m
    annotations:
      summary: "High latency detected"

  - alert: LowCreditBalance
    expr: user_credit_balance < 10
    for: 1m
    annotations:
      summary: "User credit balance low"
```

## Security Checklist

- [x] Strong SECRET_KEY set
- [x] All API keys in environment variables
- [x] SSL/TLS enabled
- [x] Database credentials secured
- [x] CORS properly configured
- [x] Rate limiting enabled
- [x] Input validation on all endpoints
- [x] Regular security updates
- [x] Firewall configured
- [x] Backup strategy in place
- [x] Monitoring and alerts set up
- [x] DDoS protection (Cloudflare recommended)

## Troubleshooting

### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart api

# Increase memory limits in docker-compose.yml
```

### Database Connection Issues

```bash
# Check connections
docker-compose exec postgres psql -U postgres -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
docker-compose exec postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity \
   WHERE state = 'idle';"
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```
