# Multi-Tenant SaaS Architecture - Implementation Guide

## 🏗️ Architecture Overview

This document describes the multi-tenant SaaS transformation of Tabbycat using Django + Vue 3.

### Key Technologies
- **Backend**: Django 5.0 + Django REST Framework + django-tenants
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router
- **Database**: PostgreSQL with schema-based isolation
- **Authentication**: JWT (Simple JWT)
- **Deployment**: Docker + Nginx (wildcard subdomain routing)

## 📊 Multi-Tenancy Model

### Schema-Based Isolation
Each user who signs up gets:
- ✅ **Own PostgreSQL schema** (e.g., `schema_john`, `schema_jane`)
- ✅ **Unique subdomain** (e.g., `john.myapp.com`, `jane.myapp.com`)
- ✅ **Isolated tenant data** (tournaments, teams, results, etc.)
- ✅ **Automatic creation** via Django signals on user registration

### Shared vs. Tenant Apps

#### Shared Apps (Public Schema)
These apps are available in ALL schemas and store global data:
- `tenants` - Client and Domain models
- `tenant_control` - Super admin dashboard backend
- `users` - User authentication and profiles
- Django core apps (`auth`, `contenttypes`, `sessions`, etc.)

#### Tenant Apps (Tenant Schemas)
These apps are isolated per tenant and store tenant-specific data:
- `tournaments` - Tournament management
- `participants` - Teams, adjudicators, speakers
- `draw` - Debate draws and matchups
- `results` - Ballot submissions and scoring
- `adjallocation` - Adjudicator allocation
- `adjfeedback` - Adjudicator feedback
- `motions` - Motion management
- `venues` - Venue management
- `breakqual` - Break qualification
- `standings` - Speaker/team standings
- All other Tabbycat tournament apps

## 🗂️ Project Structure

```
tabbycat/
├── settings/
│   ├── core.py              # Base Django settings
│   ├── tenants.py           # ✨ NEW: Multi-tenant configuration
│   ├── production.py        # Production settings (to be created)
│   ├── docker.py            # Docker settings
│   └── local.py             # Local development settings
│
├── tenants/                 # ✨ NEW: Tenant management app
│   ├── models.py            # Client and Domain models
│   ├── signals.py           # Auto-tenant creation on signup
│   ├── admin.py             # Django admin for tenants
│   └── apps.py
│
├── tenant_control/          # ✨ NEW: Super admin dashboard
│   ├── views.py             # REST API views for tenant CRUD
│   ├── serializers.py       # DRF serializers
│   ├── permissions.py       # Permission classes
│   ├── urls.py              # API endpoints
│   └── management/
│       └── commands/
│           ├── migrate_schemas.py    # Migrate all tenant schemas
│           ├── seed_demo_tenants.py  # Create demo tenants
│           └── update_tenant_stats.py # Update usage stats
│
├── users/                   # Enhanced for multi-tenancy
│   ├── models.py            # User model with tenant relationship
│   ├── serializers.py       # User registration/authentication
│   └── views.py             # JWT auth endpoints
│
├── urls.py                  # Tenant URL routing
├── urls_public.py           # ✨ NEW: Public schema URLs (admin.myapp.com)
├── asgi.py                  # ASGI configuration
└── wsgi.py                  # WSGI configuration
```

## 🔐 Authentication Flow

### JWT-Based Authentication
1. **User Registration** (`POST /auth/register/`)
   - Create user account
   - Auto-create tenant schema via signal
   - Auto-create domain (`username.myapp.com`)
   - Return JWT tokens

2. **Login** (`POST /auth/login/`)
   - Validate credentials
   - Generate access + refresh JWT tokens
   - Return user info + tenant info

3. **Token Refresh** (`POST /auth/refresh/`)
   - Validate refresh token
   - Generate new access token

4. **Authenticated Requests**
   - Include `Authorization: Bearer <token>` header
   - Django-tenants resolves tenant from subdomain
   - Middleware switches to tenant schema

## 🌐 Domain Routing

### Subdomain Structure
- `admin.myapp.com` → Public schema (super admin dashboard)
- `john.myapp.com` → John's tenant schema
- `jane.myapp.com` → Jane's tenant schema

### Nginx Configuration
```nginx
server {
    server_name *.myapp.com;
    
    location / {
        proxy_pass http://django:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📁 Database Schema Layout

### Public Schema (`public`)
```
public/
├── auth_user
├── auth_group
├── auth_permission
├── tenants_client          ← Tenant metadata
├── tenants_domain          ← Domain mappings
├── django_session
└── ... (other shared tables)
```

### Tenant Schema (e.g., `schema_john`)
```
schema_john/
├── tournaments_tournament
├── participants_team
├── participants_adjudicator
├── participants_speaker
├── draw_debate
├── results_ballotsubmission
├── adjallocation_adjudicatorallocation
└── ... (all tenant-specific tables)
```

## 🚀 Deployment Architecture

### Docker Compose Services
```yaml
services:
  db:
    image: postgres:15
    # Single database, multiple schemas
    
  redis:
    image: redis:7
    # Shared cache/sessions
    
  django:
    build: .
    command: gunicorn tabbycat.wsgi:application
    # Handles all tenant schemas dynamically
    
  worker:
    build: .
    command: python run-worker.py
    # Background tasks (Celery/Channels)
    
  nginx:
    image: nginx:alpine
    # Wildcard subdomain routing (*.myapp.com)
```

### Environment Variables
```bash
# Django
DJANGO_SETTINGS_MODULE=settings.tenants
SECRET_KEY=<strong-secret-key>

# Database
DATABASE_URL=postgresql://user:pass@db:5432/tabbycat

# Tenants
TENANT_BASE_DOMAIN=myapp.com
ADMIN_SUBDOMAIN=admin

# CORS (for Vue frontend)
CORS_ALLOWED_ORIGINS=https://admin.myapp.com,https://*.myapp.com

# JWT
JWT_SECRET_KEY=<separate-jwt-secret>
```

## 🎨 Frontend Architecture

### Vue 3 Tenant SPA
Located at each tenant subdomain (e.g., `john.myapp.com`):
```
frontend-tenant/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js        # Vue Router config
│   ├── stores/
│   │   ├── auth.js         # Pinia auth store
│   │   └── tenant.js       # Tenant data store
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── Tournaments.vue
│   │   ├── Teams.vue
│   │   └── Results.vue
│   ├── components/
│   │   ├── Layout/
│   │   ├── Forms/
│   │   └── Charts/
│   └── api/
│       └── client.js       # Axios API client with JWT
├── vite.config.js
└── package.json
```

### Vue 3 Super Admin Dashboard
Located at `admin.myapp.com`:
```
frontend-admin/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   └── admin.js        # Admin store
│   ├── views/
│   │   ├── TenantList.vue       # List all tenants
│   │   ├── TenantDetail.vue     # Tenant details + actions
│   │   ├── Analytics.vue        # Usage analytics
│   │   └── Settings.vue         # Admin settings
│   └── components/
│       ├── TenantCard.vue
│       ├── StatsChart.vue
│       └── ActionButtons.vue   # Suspend/Delete/Impersonate
├── vite.config.js
└── package.json
```

## 🔧 Management Commands

### Migrate All Schemas
```bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant
```

### Create Demo Tenants
```bash
python manage.py seed_demo_tenants --count 5
```

### Update Tenant Stats
```bash
python manage.py update_tenant_stats
```

## 📊 Super Admin Dashboard Features

### Tenant Management
- ✅ **List all tenants** with pagination, search, filters
- ✅ **View tenant details** (owner, domains, usage stats)
- ✅ **Suspend/unsuspend** tenants
- ✅ **Delete tenants** (with confirmation)
- ✅ **Impersonate tenants** (generate JWT to access their site)
- ✅ **Update tenant info** (plan, notes, status)

### Analytics
- ✅ **Total tenants** (active, suspended, inactive)
- ✅ **Storage usage** (per tenant, total)
- ✅ **User counts** (per tenant, total)
- ✅ **Tournament counts** (per tenant, total)
- ✅ **Recent signups** (last 7/30 days)
- ✅ **Tenants by plan** (free, basic, pro, enterprise)
- ✅ **Activity timeline** (recent tenant activity)

## 🔒 Security Considerations

### Tenant Isolation
- ✅ PostgreSQL schema-level isolation (strongest isolation without separate DBs)
- ✅ Row-level security via schema context
- ✅ No cross-tenant queries possible
- ✅ Middleware enforces schema switching based on subdomain

### Authentication
- ✅ JWT tokens with short expiration (1 hour access, 7 days refresh)
- ✅ Token rotation on refresh
- ✅ Blacklisting on logout
- ✅ HTTPS-only in production
- ✅ Secure cookies for sessions

### API Security
- ✅ CORS configured for specific origins
- ✅ CSRF protection for non-API requests
- ✅ Rate limiting (to be implemented)
- ✅ Permission classes (IsAuthenticated, IsSuperAdmin)

## 📚 API Endpoints

### Public API (`admin.myapp.com`)
```
POST   /auth/register/              # User registration + tenant creation
POST   /auth/login/                 # JWT login
POST   /auth/refresh/               # Refresh access token
POST   /auth/logout/                # Logout (blacklist token)
GET    /auth/me/                    # Get current user info
```

### Super Admin API (`admin.myapp.com/api/admin/`)
```
GET    /api/admin/tenants/          # List all tenants
POST   /api/admin/tenants/          # Create tenant manually
GET    /api/admin/tenants/{id}/     # Tenant details
PATCH  /api/admin/tenants/{id}/     # Update tenant
DELETE /api/admin/tenants/{id}/     # Delete tenant
POST   /api/admin/tenants/{id}/suspend/     # Suspend tenant
POST   /api/admin/tenants/{id}/unsuspend/   # Unsuspend tenant
POST   /api/admin/tenants/{id}/impersonate/ # Get impersonation JWT
GET    /api/admin/stats/            # Global statistics
GET    /api/admin/analytics/        # Detailed analytics
```

### Tenant API (`{tenant}.myapp.com/api/`)
```
GET    /api/tournaments/            # List tournaments
POST   /api/tournaments/            # Create tournament
GET    /api/teams/                  # List teams
POST   /api/teams/                  # Create team
GET    /api/adjudicators/           # List adjudicators
... (all existing Tabbycat API endpoints)
```

## 🛠️ Development Workflow

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# or
pipenv install
```

### 2. Set Up Database
```bash
# Create database
createdb tabbycat_multitenant

# Run migrations for public schema
python manage.py migrate_schemas --shared

# Create superuser (for admin.myapp.com)
python manage.py createsuperuser
```

### 3. Create Test Tenants
```bash
# Seed demo tenants
python manage.py seed_demo_tenants --count 3
```

### 4. Run Development Server
```bash
# Django
python manage.py runserver

# Vue (tenant SPA)
cd frontend-tenant
npm run dev

# Vue (admin SPA)
cd frontend-admin
npm run dev
```

### 5. Access the System
- Super admin: `http://admin.localhost:8000`
- Tenant 1: `http://john.localhost:8000`
- Tenant 2: `http://jane.localhost:8000`

## 🚀 Production Deployment

### 1. Build Frontend
```bash
cd frontend-tenant
npm run build  # → dist/

cd ../frontend-admin
npm run build  # → dist/
```

### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 3. Migrate All Schemas
```bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant
```

### 4. Start Services
```bash
docker-compose up -d
```

### 5. Configure DNS
```
A     @             → server_ip
A     *             → server_ip (wildcard for subdomains)
```

## 📈 Scalability Considerations

### Database
- ✅ Schema-based isolation (thousands of tenants possible)
- ✅ Connection pooling (pgbouncer recommended)
- ✅ Query optimization per tenant
- ⚠️ Large tenant counts may require schema pruning/archival

### Caching
- ✅ Redis for shared cache (sessions, auth)
- ✅ Per-tenant caching with schema prefix
- ✅ CDN for static assets

### Performance
- ✅ Database indexes on tenant lookups
- ✅ Lazy schema loading
- ✅ Async workers for background tasks
- ✅ Gunicorn with multiple workers

## 🧪 Testing

### Unit Tests
```bash
python manage.py test --settings=settings.tenants
```

### Tenant Isolation Tests
```bash
python manage.py test tenants.tests
```

### API Tests
```bash
pytest api/tests/
```

## 📝 Configuration Checklist

### Before Production
- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL/TLS certificates (Let's Encrypt)
- [ ] Configure `CORS_ALLOWED_ORIGINS` properly
- [ ] Enable Sentry or error logging
- [ ] Set up database backups
- [ ] Configure email (SMTP)
- [ ] Set tenant usage limits
- [ ] Enable rate limiting
- [ ] Configure Celery for async tasks
- [ ] Set up monitoring (Prometheus, Grafana)

## 🆘 Troubleshooting

### Schema Not Found
```bash
# Recreate tenant schema
python manage.py tenant_command create_tenant --schema_name=john
```

### Domain Routing Issues
```bash
# Check domain mappings
python manage.py shell
>>> from tenants.models import Domain
>>> Domain.objects.all()
```

### Migration Issues
```bash
# Migrate specific tenant
python manage.py migrate_schemas --schema=john

# Drop and recreate schema (⚠️ DATA LOSS)
python manage.py tenant_command delete_tenant --schema_name=john
```

## 📖 Additional Resources

- [Django-Tenants Documentation](https://django-tenants.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia (Vue Store)](https://pinia.vuejs.org/)

## 🎯 Next Steps

1. **Complete Backend Implementation**
   - Finish tenant_control views
   - Create management commands
   - Add JWT authentication endpoints

2. **Build Vue Frontends**
   - Set up Vite projects
   - Create authentication flow
   - Build tenant dashboard
   - Build super admin dashboard

3. **Update Docker Configuration**
   - Add Nginx wildcard routing
   - Configure environment variables
   - Set up multi-stage builds

4. **Testing & QA**
   - Unit tests for tenant isolation
   - Integration tests for API
   - E2E tests with Cypress/Playwright

5. **Documentation**
   - User guide for tenant owners
   - API documentation (Swagger/ReDoc)
   - Deployment guide
   - Admin guide

## 📞 Support

For issues or questions about this multi-tenant architecture, refer to:
- Project documentation in `/docs`
- Django-tenants issues on GitHub
- Tabbycat community forums

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Author**: Tabbycat Multi-Tenant Team
