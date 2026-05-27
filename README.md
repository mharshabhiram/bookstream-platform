# 📚 BookStream — Premium Ebook Platform

A production-ready, Netflix-inspired ebook reading platform built with modern web technologies.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BOOKSTREAM PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Next.js    │    │   FastAPI    │    │   Celery     │                  │
│  │   Frontend   │◄──►│   Backend    │◄──►│   Workers    │                  │
│  │   (PWA)      │    │   (API)      │    │   (Async)    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Redis      │    │  PostgreSQL  │    │  S3/R2       │                  │
│  │   (Cache)    │    │   (Primary)  │    │  (Storage)   │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo>
cd ebook-platform

# Environment setup
cp .env.example .env

# Start all services
docker compose -f infra/docker/docker-compose.yml up -d

# Run migrations
docker compose exec api alembic upgrade head

# Access the app
# Web: http://localhost:3000
# API: http://localhost:8000/docs
```

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, ShadCN UI, Framer Motion |
| Backend | FastAPI, SQLAlchemy 2.0, asyncpg, Celery |
| Database | PostgreSQL 16, Redis 7 |
| Storage | S3-compatible (AWS S3 / Cloudflare R2 / MinIO) |
| Auth | JWT + OAuth2 (Google, GitHub) |
| Ebook | EPUB.js, PDF.js |
| DevOps | Docker, Nginx, GitHub Actions |

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security](docs/SECURITY.md)

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
