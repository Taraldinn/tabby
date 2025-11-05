# Dokploy Deployment Guide for Tabbycat

This guide will help you deploy Tabbycat on Dokploy, a self-hosted Platform as a Service (PaaS).

## Prerequisites

- Dokploy instance running and accessible
- Domain name (optional but recommended)
- Git repository access

## Quick Start

### 1. Prepare Your Dokploy Instance

1. Install Dokploy on your server:
   ```bash
   curl -sSL https://dokploy.com/install.sh | sh
   ```

2. Access Dokploy dashboard at `http://your-server-ip:3000`

### 2. Create New Application

1. In Dokploy dashboard, click "Create Application"
2. Choose "Docker Compose" as deployment method
3. Connect your Git repository
4. Select branch: `master`
5. Set compose file path: `docker-compose.dokploy.yml`

### 3. Environment Variables

Add these environment variables in Dokploy dashboard:

**Required:**
```bash
SECRET_KEY=your-random-50-character-secret-key
POSTGRES_PASSWORD=your-secure-database-password
```

**Optional Email Configuration:**
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=1
```

**Optional Site Configuration:**
```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=your-admin-password
```

### 4. Generate Secret Key

Generate a secure SECRET_KEY:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Deploy

1. Click "Deploy" in Dokploy dashboard
2. Monitor build logs
3. Wait for all services to be healthy

### 6. Access Your Application

After successful deployment:
- Main app: `http://your-domain` or `http://your-server-ip`
- Admin panel: `http://your-domain/database/`

Default credentials (if set via env vars):
- Username: `admin` (or your DJANGO_SUPERUSER_USERNAME)
- Password: (your DJANGO_SUPERUSER_PASSWORD)

## Architecture

The deployment includes:

- **Web**: Django application with Gunicorn (Port 8000)
- **Worker**: Background task processor
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Nginx**: Reverse proxy and static file server (Port 80)

## Domain Configuration

### Using Dokploy's Built-in Proxy

1. Go to your application settings
2. Click "Domains"
3. Add your domain: `yourdomain.com`
4. Dokploy will automatically configure SSL with Let's Encrypt

### Manual DNS Configuration

Point your domain to your Dokploy server:
```
A Record: @ -> your-server-ip
A Record: www -> your-server-ip
```

## Post-Deployment Setup

### 1. Create Tournaments

1. Log in to admin panel
2. Navigate to main site
3. Click "Create Tournament"
4. Import tournament data or create manually

### 2. Configure Email (if not done via env vars)

Go to Admin Panel → Dynamic Preferences and configure:
- Email host settings
- Email templates
- Notification preferences

### 3. Backup Configuration

Set up regular backups:

```bash
# Backup database
docker exec tabbycat-db-1 pg_dump -U tabbycat tabbycat > backup.sql

# Restore database
docker exec -i tabbycat-db-1 psql -U tabbycat tabbycat < backup.sql
```

## Scaling

### Horizontal Scaling

In Dokploy dashboard, you can scale services:

1. Go to application settings
2. Click "Scale"
3. Increase replicas for:
   - **Web**: Handle more concurrent users
   - **Worker**: Process background tasks faster

### Vertical Scaling

Adjust resource limits in `docker-compose.dokploy.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring

### Health Checks

All services have health checks configured:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`

### Logs

View logs in Dokploy dashboard or via CLI:

```bash
# All services
docker-compose -f docker-compose.dokploy.yml logs -f

# Specific service
docker-compose -f docker-compose.dokploy.yml logs -f web
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database container
docker-compose -f docker-compose.dokploy.yml ps db

# Check database logs
docker-compose -f docker-compose.dokploy.yml logs db

# Verify connection
docker-compose -f docker-compose.dokploy.yml exec web python manage.py dbshell
```

### Static Files Not Loading

```bash
# Recollect static files
docker-compose -f docker-compose.dokploy.yml exec web python manage.py collectstatic --noinput
```

### Worker Not Processing Tasks

```bash
# Check worker logs
docker-compose -f docker-compose.dokploy.yml logs worker

# Restart worker
docker-compose -f docker-compose.dokploy.yml restart worker
```

### Reset Admin Password

```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py changepassword admin
```

## Maintenance

### Update Application

1. Push changes to Git repository
2. In Dokploy dashboard, click "Redeploy"
3. Monitor deployment logs

### Database Migrations

Migrations run automatically on deployment. To run manually:

```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py migrate
```

### Clear Cache

```bash
docker-compose -f docker-compose.dokploy.yml exec redis redis-cli FLUSHALL
```

## Security Best Practices

1. **Change default passwords** immediately after deployment
2. **Use strong SECRET_KEY** (50+ random characters)
3. **Enable SSL/HTTPS** via Dokploy's domain settings
4. **Set DEBUG=0** in production
5. **Restrict ALLOWED_HOSTS** to your actual domains
6. **Regular backups** of database and media files
7. **Keep services updated** via Dokploy

## Performance Optimization

### Database

Add indexes for better performance:
```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py dbshell
```

### Redis

Configure Redis persistence in `docker-compose.dokploy.yml`:
```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Nginx Caching

Static files are served by Nginx with aggressive caching for better performance.

## Support

- **Dokploy Docs**: https://docs.dokploy.com
- **Tabbycat Docs**: https://tabbycat.readthedocs.io
- **Issues**: https://github.com/TabbycatDebate/tabbycat/issues

## Migration from Other Platforms

### From Heroku/Render

1. Export database:
   ```bash
   heroku pg:backups:capture
   heroku pg:backups:download
   ```

2. Import to Dokploy:
   ```bash
   docker exec -i tabbycat-db-1 psql -U tabbycat tabbycat < latest.dump
   ```

3. Update environment variables in Dokploy

4. Deploy!

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
