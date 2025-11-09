# Multi-Tenant SaaS Setup Guide

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for Vue frontends)

### 1. Install Backend Dependencies

```bash
# Using pipenv (recommended)
pipenv install

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```bash
# Django Settings
DJANGO_SETTINGS_MODULE=settings.tenants
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=postgresql://tabbycat:password@localhost:5432/tabbycat_multi

# Redis
REDIS_URL=redis://localhost:6379/0

# Multi-Tenant Configuration
TENANT_BASE_DOMAIN=localhost:8000
ADMIN_SUBDOMAIN=admin

# JWT
JWT_SECRET_KEY=your-jwt-secret-here

# CORS (for development)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Create Database

```bash
createdb tabbycat_multi
```

### 4. Run Initial Migrations

```bash
# Migrate public schema (shared apps)
python tabbycat/manage.py migrate_schemas --shared

# Create superuser for admin dashboard
python tabbycat/manage.py createsuperuser
```

### 5. Create Demo Tenants (Optional)

```bash
# Create 3 demo tenants with sample data
python tabbycat/manage.py seed_demo_tenants --count 3
```

### 6. Run Development Server

```bash
# Django backend
python tabbycat/manage.py runserver 0.0.0.0:8000

# In another terminal: Vue tenant frontend
cd frontend-tenant
npm install
npm run dev

# In another terminal: Vue admin frontend
cd frontend-admin
npm install
npm run dev
```

### 7. Access the System

- **Super Admin Dashboard**: http://admin.localhost:8000
- **Tenant Sites**: http://[username].localhost:8000
  - Example: http://john.localhost:8000

### 8. Test API Endpoints

```bash
# Register a new user (auto-creates tenant)
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secure123"}'

# Login and get JWT
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123"}'

# Access tenant API (use JWT from login)
curl http://alice.localhost:8000/api/tournaments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Production Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate_schemas --shared
docker-compose exec web python manage.py migrate_schemas --tenant

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Environment Variables (Production)

```bash
# Django
DJANGO_SETTINGS_MODULE=settings.production
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=.myapp.com

# Database
DATABASE_URL=postgresql://user:pass@db:5432/tabbycat

# Redis
REDIS_URL=redis://redis:6379/0

# Multi-Tenant
TENANT_BASE_DOMAIN=myapp.com
ADMIN_SUBDOMAIN=admin

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://admin.myapp.com,https://*.myapp.com

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@myapp.com
EMAIL_HOST_PASSWORD=<app-password>
EMAIL_USE_TLS=True
```

## DNS Configuration

### Wildcard Subdomain

Set up an A record and wildcard A record:

```
@    A    server_ip
*    A    server_ip
```

This allows:
- `myapp.com` → main site
- `admin.myapp.com` → super admin dashboard
- `alice.myapp.com` → Alice's tenant site
- `bob.myapp.com` → Bob's tenant site

## Nginx Configuration

```nginx
# /etc/nginx/sites-available/tabbycat-multi

server {
    listen 80;
    server_name *.myapp.com;

    # Redirect to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name *.myapp.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Management Commands

### Migrate All Tenant Schemas

```bash
# Migrate only shared apps (public schema)
python manage.py migrate_schemas --shared

# Migrate all tenant schemas
python manage.py migrate_schemas --tenant

# Migrate specific tenant
python manage.py migrate_schemas --schema=alice
```

### Update Tenant Usage Statistics

```bash
# Update all tenants
python manage.py update_tenant_stats

# Update specific tenant
python manage.py update_tenant_stats --tenant=alice
```

### Create Demo Tenants

```bash
# Create 5 demo tenants
python manage.py seed_demo_tenants --count 5
```

### Delete Tenant (⚠️ DESTRUCTIVE)

```bash
# Delete tenant and all data
python manage.py delete_tenant --schema=alice
```

## Monitoring & Maintenance

### Check Tenant Health

```bash
# List all tenants
python manage.py shell
>>> from tenants.models import Client
>>> Client.objects.all()

# Check domain mappings
>>> from tenants.models import Domain
>>> Domain.objects.all()
```

### Database Backup

```bash
# Backup all schemas
pg_dump -U tabbycat tabbycat_multi > backup.sql

# Backup specific schema
pg_dump -U tabbycat -n schema_alice tabbycat_multi > alice_backup.sql

# Restore
psql -U tabbycat tabbycat_multi < backup.sql
```

### Performance Optimization

```bash
# Analyze database
python manage.py dbshell
=> ANALYZE;

# Vacuum database
=> VACUUM ANALYZE;

# Check schema sizes
=> SELECT schema_name, 
          pg_size_pretty(sum(table_size)::bigint) as size
   FROM (
     SELECT pg_catalog.pg_namespace.nspname as schema_name,
            pg_relation_size(pg_catalog.pg_class.oid) as table_size
     FROM pg_catalog.pg_class
     JOIN pg_catalog.pg_namespace ON relnamespace = pg_catalog.pg_namespace.oid
   ) t
   GROUP BY schema_name
   ORDER BY sum(table_size) DESC;
```

## Troubleshooting

### Tenant Schema Not Created

```bash
# Manually create schema
python manage.py shell
>>> from tenants.models import Client
>>> tenant = Client.objects.get(schema_name='alice')
>>> tenant.create_schema()
```

### Domain Routing Not Working

Check:
1. DNS wildcard record is configured
2. Nginx is proxying all subdomains
3. `TENANT_BASE_DOMAIN` matches your domain
4. Domain exists in database

```bash
python manage.py shell
>>> from tenants.models import Domain
>>> Domain.objects.filter(domain__contains='alice')
```

### Migration Errors

```bash
# Fake migrations for specific tenant (⚠️ use carefully)
python manage.py migrate_schemas --schema=alice --fake

# Reset migrations
python manage.py migrate_schemas --schema=alice tournaments zero
python manage.py migrate_schemas --schema=alice tournaments
```

### JWT Token Issues

```bash
# Test JWT generation
python manage.py shell
>>> from rest_framework_simplejwt.tokens import RefreshToken
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='alice')
>>> refresh = RefreshToken.for_user(user)
>>> print(str(refresh.access_token))
```

## Security Best Practices

1. **Always use HTTPS in production**
2. **Strong SECRET_KEY and JWT_SECRET_KEY** (generate with `django-admin startproject` or `secrets.token_urlsafe(50)`)
3. **Enable HSTS** (Strict-Transport-Security header)
4. **Configure CORS properly** (don't use `CORS_ALLOW_ALL_ORIGINS = True` in production)
5. **Rate limiting** (use django-ratelimit or similar)
6. **Regular backups** (automated daily backups)
7. **Monitor for suspicious activity** (failed login attempts, unusual API usage)
8. **Keep dependencies updated** (security patches)

## Getting Help

- Read `MULTI_TENANT_ARCHITECTURE.md` for detailed architecture docs
- Check Django-tenants documentation: https://django-tenants.readthedocs.io/
- Tabbycat community forums
- GitHub issues

---

Happy multi-tenanting! 🚀
