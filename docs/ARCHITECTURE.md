# BookStream Architecture

## System Overview

BookStream is a modern ebook reading platform built with a microservices-inspired architecture using:

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS + Framer Motion
- **Backend**: FastAPI + SQLAlchemy 2.0 + asyncpg + Celery
- **Database**: PostgreSQL 16 (primary) + Redis 7 (cache/queue)
- **Storage**: S3-compatible (AWS S3 / Cloudflare R2 / MinIO)
- **Search**: PostgreSQL full-text search + optional Elasticsearch
- **Auth**: JWT + OAuth2 (Google, GitHub)

## High-Level Architecture

```
Client Layer (Browser/PWA)
    |
    v HTTPS
Nginx Gateway (SSL, Rate Limit, Cache)
    |
    +---> Next.js Frontend (SSR, Static Gen, PWA)
    |
    +---> FastAPI Backend (REST API, Auth, Business Logic)
              |
              +---> PostgreSQL 16 (Users, Books, Reading Data)
              +---> Redis 7 (Sessions, Cache, Celery Queue)
              +---> S3/R2 (Book Files, Covers, Avatars)
              +---> Celery Workers (Ebook Processing, Emails, Analytics)
```

## Database Schema Highlights

### Core Tables
- `users` — Accounts, profiles, roles, OAuth links
- `books` — Ebook metadata, file info, cover URLs
- `authors` — Author profiles with slug-based URLs
- `categories` — Hierarchical genre taxonomy
- `user_books` — Library entries with reading status
- `reading_progress` — Per-book progress tracking
- `highlights` — Text selections with colors and notes
- `bookmarks` — Saved positions with labels
- `notes` — User annotations with tags
- `reviews` — Ratings and written reviews
- `shelves` — Custom user collections
- `collections` — Public curated reading lists
- `follows` — Social following relationships
- `notifications` — In-app notification queue
- `reading_sessions` — Detailed analytics events
- `daily_reading_stats` — Aggregated daily metrics

### Indexing Strategy
- B-tree indexes on `users.email`, `users.username`, `books.slug`
- GIN indexes for full-text search on `books.title`, `books.description`
- Composite indexes for common query patterns
- Partial indexes for filtered queries (featured, public)

## Security Architecture

### Authentication
- JWT access tokens (30 min expiry) + refresh tokens (7 day expiry)
- Secure HTTP-only cookies with SameSite=strict
- Bcrypt password hashing (12 rounds)
- OAuth 2.0 with PKCE for Google/GitHub
- Device tracking with session management
- Account lockout after 5 failed attempts

### Authorization
- RBAC: User -> Moderator -> Admin
- Resource-level permissions (own vs. public books)
- API rate limiting per endpoint

### Data Protection
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention with React auto-escaping
- CSRF protection via SameSite cookies
- Content Security Policy headers
- File upload validation (type, size, magic bytes)

## Performance Optimizations

### Caching Strategy
- Redis for session storage (TTL: 30 min)
- Redis for API response caching (TTL: 5 min)
- Browser caching for static assets (1 year)
- CDN for book covers and avatars

### Database
- Connection pooling (asyncpg)
- Query result caching with Redis
- Lazy loading of relationships
- Pagination on all list endpoints

### Frontend
- Next.js image optimization (WebP, responsive)
- Code splitting by route
- Service worker for offline reading
- Virtualized lists for large libraries
- Skeleton loading states

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (no local state)
- Shared Redis for sessions/cache
- PostgreSQL read replicas for queries
- Celery workers scale independently

### File Storage
- S3-compatible object storage
- Presigned URLs for direct uploads
- CloudFront/Cloudflare CDN for delivery

## Monitoring & Observability

- Structured JSON logging with correlation IDs
- Prometheus metrics for API performance
- Health check endpoints for load balancers
- Distributed tracing with OpenTelemetry
