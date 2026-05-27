# BookStream Security Guide

## Authentication & Authorization

### JWT Implementation
- **Access Tokens**: HS256, 30-minute expiry, contains user ID + role
- **Refresh Tokens**: HS256, 7-day expiry, stored hashed in database
- **Token Storage**: HTTP-only cookies with Secure and SameSite=Strict
- **Token Rotation**: New refresh token issued on each refresh

### Password Security
- Bcrypt with 12 rounds (adaptive, ~250ms per hash)
- Minimum requirements: 8 chars, 1 uppercase, 1 lowercase, 1 digit
- Password history prevents reuse of last 5 passwords
- Secure password reset via time-limited tokens (1 hour)

### OAuth Security
- PKCE flow for all OAuth providers
- State parameter validation
- Provider account linking with email verification
- No password required for OAuth-only accounts

## API Security

### Rate Limiting
- General API: 60 requests/minute per IP
- Auth endpoints: 5 requests/minute per IP
- Upload endpoints: 10 requests/hour per user
- Implemented via Redis sliding window

### Input Validation
- All inputs validated with Pydantic schemas
- File uploads: magic bytes check, size limits (100MB)
- Path traversal prevention in file storage
- SQL injection prevention via parameterized queries

### Headers & Transport
- HSTS enabled (max-age=31536000, includeSubDomains)
- Content-Security-Policy with strict directives
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- TLS 1.3 required in production

## Data Protection

### Encryption
- Database connections via TLS
- File storage encryption at rest (S3 SSE)
- JWT secrets rotated quarterly
- Backup encryption with GPG

### Privacy
- GDPR-compliant data deletion
- User data export (JSON format)
- Consent tracking for analytics
- Minimal data collection principle

### Audit Logging
- All auth events logged (login, logout, password change)
- Admin actions logged with before/after states
- Failed access attempts tracked
- 90-day log retention

## Vulnerability Prevention

| Threat | Mitigation |
|--------|-----------|
| SQL Injection | SQLAlchemy ORM, parameterized queries |
| XSS | React auto-escaping, CSP, input sanitization |
| CSRF | SameSite cookies, token validation |
| Insecure Deserialization | JSON only, schema validation |
| File Upload | Magic bytes, size limits, virus scanning hooks |
| DoS | Rate limiting, request timeouts, connection pooling |
| IDOR | Resource ownership checks on every endpoint |
| Mass Assignment | Explicit Pydantic schemas, no wildcard updates |

## Incident Response

1. **Detection**: Automated alerts on anomaly patterns
2. **Containment**: Rate limiting, IP blocking, session revocation
3. **Investigation**: Audit log analysis, correlation IDs
4. **Recovery**: Token rotation, password resets, notification
5. **Post-Incident**: Security review, process improvement
