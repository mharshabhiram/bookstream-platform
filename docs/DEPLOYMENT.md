# BookStream Deployment Guide

## Quick Start (Docker Compose)

```bash
# 1. Clone the repository
git clone <repo-url>
cd ebook-platform

# 2. Create environment file
cp .env.example .env
# Edit .env with your settings

# 3. Start all services
docker compose -f infra/docker/docker-compose.yml up -d

# 4. Run database migrations
docker compose exec api alembic upgrade head

# 5. Access the application
# Web: http://localhost
# API: http://localhost/api/docs
# MinIO Console: http://localhost:9001
```

## Production Deployment

### Prerequisites
- Docker & Docker Compose
- Domain with DNS configured
- SSL certificates (Let's Encrypt)
- Server with 4GB+ RAM, 2+ CPU cores

### VPS Deployment (DigitalOcean / Hetzner / Linode)

```bash
# On your server:
# 1. Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# 2. Clone and configure
git clone <repo-url> /opt/bookstream
cd /opt/bookstream
cp .env.example .env
# Edit production values

# 3. Generate secrets
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -hex 16)

# 4. Start services
docker compose -f infra/docker/docker-compose.yml up -d

# 5. Setup SSL with Certbot
sudo certbot --nginx -d bookstream.io -d www.bookstream.io

# 6. Setup backups
# Add cron job for database backups
0 2 * * * docker exec bookstream-postgres pg_dump -U bookstream bookstream > /backups/bookstream-$(date +%Y%m%d).sql
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | Yes | Secret key for JWT signing |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `STORAGE_TYPE` | No | `local`, `s3`, or `r2` (default: local) |
| `STORAGE_BUCKET` | No | S3/R2 bucket name |
| `STORAGE_ACCESS_KEY` | No | S3/R2 access key |
| `STORAGE_SECRET_KEY` | No | S3/R2 secret key |
| `SMTP_HOST` | No | Email server host |
| `SMTP_USER` | No | Email username |
| `SMTP_PASSWORD` | No | Email password |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | No | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | No | GitHub OAuth client secret |

## Monitoring & Logging

- **Prometheus** metrics exposed at `/metrics`
- **Structured logging** with `structlog`
- **Health checks** at `/health`
- Set up **Sentry** for error tracking
- Use **Grafana** + **Loki** for log aggregation

## Backup Strategy

1. **Database**: Daily automated backups via `pg_dump`
2. **Files**: S3/R2 versioning for uploaded books
3. **Disaster Recovery**: Point-in-time recovery with WAL archiving
