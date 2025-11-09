# Local Development Setup - Complete ✅

## Database Configuration

**Database Name**: `tabbycat_multi`  
**Connection**: PostgreSQL with peer authentication (Unix socket)  
**Status**: ✅ Created and migrated

## What's Been Set Up

### 1. Database Created
```bash
createdb tabbycat_multi
```

### 2. Migrations Applied
All Django migrations have been successfully applied to the `tabbycat_multi` database.

### 3. Superuser Created
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: (Set using Django admin panel or `python tabbycat/manage.py changepassword admin`)

### 4. Configuration Files Updated
- `tabbycat/settings/local.py` - Configured for PostgreSQL peer authentication
- Multi-tenant settings are present but commented out for initial setup

## How to Run

### Start the Development Server
```bash
cd /home/aldinn/Documents/code/tabbycat
python tabbycat/manage.py runserver 0.0.0.0:8000
```

### Access the Application
- **Main Site**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
  - Login with username: `admin`
  - Set password first: `python tabbycat/manage.py changepassword admin`

## Next Steps: Enable Multi-Tenancy

The multi-tenant infrastructure is ready but currently disabled. To enable it:

### 1. Uncomment Multi-Tenant Settings
Edit `tabbycat/settings/local.py` and uncomment the multi-tenant configuration section (lines ~66-110)

### 2. Update Database Engine
Change the database engine from:
```python
"ENGINE": "django.db.backends.postgresql"
```
to:
```python
"ENGINE": "django_tenants.postgresql_backend"
```

### 3. Create Tenant Models Migration
```bash
python tabbycat/manage.py makemigrations tenants tenant_control
python tabbycat/manage.py migrate --shared
```

### 4. Create Your First Tenant
```python
python tabbycat/manage.py shell

from tenants.models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

# Create or get a user
user = User.objects.first()  # or create new user

# Create tenant
tenant = Client.objects.create(
    schema_name='john',
    name="John's Tournament Site",
    owner=user
)

# Create domain
Domain.objects.create(
    domain='john.localhost:8000',
    tenant=tenant,
    is_primary=True
)
```

### 5. Migrate Tenant Schema
```bash
python tabbycat/manage.py migrate_schemas --schema=john
```

### 6. Access Tenant Site
Open: http://john.localhost:8000

## Database Connection Details

The current configuration uses PostgreSQL peer authentication:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tabbycat_multi",
        "USER": "",      # Empty for peer auth
        "PASSWORD": "",  # Empty for peer auth
        "HOST": "",      # Empty uses Unix socket
        "PORT": "",      # Empty uses default
        "CONN_MAX_AGE": None,
    }
}
```

This works because:
- PostgreSQL is configured with peer authentication
- Your system user matches a PostgreSQL role
- Connection happens via Unix socket (not TCP)

## Useful Commands

### Database Operations
```bash
# Connect to database
psql -d tabbycat_multi

# Backup database
pg_dump tabbycat_multi > backup.sql

# Restore database
psql -d tabbycat_multi < backup.sql

# Drop and recreate (⚠️ destroys all data)
dropdb tabbycat_multi && createdb tabbycat_multi
```

### Django Management
```bash
# Run migrations
python tabbycat/manage.py migrate

# Create superuser
python tabbycat/manage.py createsuperuser

# Change password
python tabbycat/manage.py changepassword admin

# Django shell
python tabbycat/manage.py shell

# Collect static files
python tabbycat/manage.py collectstatic
```

## Troubleshooting

### Connection Refused
If you get "connection refused" errors:
```bash
# Check PostgreSQL status
systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Permission Denied
If you get permission errors:
```bash
# Check your PostgreSQL role
psql -c "\du"

# Create role if needed
sudo -u postgres createuser -s $USER
```

### Port Already in Use
If port 8000 is busy:
```bash
# Use a different port
python tabbycat/manage.py runserver 0.0.0.0:8080
```

## Development Workflow

1. **Make Code Changes** - Edit Python/template files
2. **Migrations** - Run `makemigrations` and `migrate` after model changes
3. **Test** - Visit http://localhost:8000 to test changes
4. **Debug** - Check terminal output for errors
5. **Commit** - Git commit your changes

## What's Working Now

✅ PostgreSQL database created  
✅ All migrations applied  
✅ Superuser created  
✅ Development server runs  
✅ Admin panel accessible  
✅ Basic Tabbycat functionality  

## What's Next (Multi-Tenant)

⏳ Enable django-tenants configuration  
⏳ Create tenant and domain models  
⏳ Set up subdomain routing  
⏳ Build JWT authentication  
⏳ Create Vue frontends  
⏳ Super admin dashboard  

---

**Status**: ✅ Ready for development  
**Date**: November 9, 2025  
**Database**: tabbycat_multi (PostgreSQL)
