# 🚀 Tabbycat on Dokploy - Quick Start

Deploy Tabbycat debate tournament software on your own Dokploy instance in minutes!

## What is Dokploy?

Dokploy is a self-hosted, open-source Platform as a Service (PaaS) that makes it easy to deploy and manage applications using Docker. Think Heroku/Render, but you own the infrastructure.

## Prerequisites

✅ A server (VPS) with Docker installed  
✅ Dokploy installed ([Installation Guide](https://docs.dokploy.com))  
✅ Domain name (optional but recommended)  

## Quick Deploy (3 Steps)

### 1️⃣ Create Application in Dokploy

1. Open Dokploy dashboard: `http://your-server:3000`
2. Click **"Create Application"**
3. Choose **"Docker Compose"**
4. Connect this Git repository
5. Set compose file: `docker-compose.dokploy.yml`

### 2️⃣ Configure Environment

Add these variables in Dokploy:

```bash
# Required
SECRET_KEY=<generate-with-command-below>
POSTGRES_PASSWORD=your-secure-password

# Optional
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ALLOWED_HOSTS=yourdomain.com
```

**Generate SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3️⃣ Deploy!

Click **"Deploy"** and wait ~3-5 minutes.

Access your site at: `http://your-domain` or `http://your-server-ip`

## What Gets Deployed?

- 🌐 **Web Server** (Django + Gunicorn)
- 👷 **Background Worker** (Task processing)
- 🗄️ **PostgreSQL 15** (Database)
- 🔴 **Redis 7** (Cache & Sessions)
- 🌍 **Nginx** (Reverse proxy & static files)

## Post-Deployment

### Create Admin User

If you didn't set superuser env vars:

```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py createsuperuser
```

### Access Admin Panel

Navigate to: `http://your-domain/database/`

### Create Your First Tournament

1. Log in to admin panel
2. Go to main site
3. Click "Create Tournament"
4. Import data or set up manually

## Local Testing (Optional)

Test before deploying to Dokploy:

```bash
# 1. Copy environment template
cp .env.dokploy.example .env

# 2. Edit .env with your settings
nano .env

# 3. Run locally
./deploy-dokploy.sh
# Choose option 2 for local testing

# 4. Access at http://localhost
```

## Scaling

### Horizontal Scaling (More Instances)

In Dokploy dashboard:
- Go to your application
- Click "Scale"
- Increase replicas for `web` and `worker`

### Vertical Scaling (More Resources)

Edit `docker-compose.dokploy.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Domain & SSL

### Add Domain

1. In Dokploy, go to application settings
2. Click "Domains"
3. Add: `yourdomain.com`
4. Dokploy auto-configures SSL with Let's Encrypt! 🔒

### DNS Configuration

Point domain to your server:
```
A Record: @ -> your-server-ip
A Record: www -> your-server-ip
```

## Backup & Restore

### Backup Database

```bash
docker exec tabbycat-db-1 pg_dump -U tabbycat tabbycat > backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker exec -i tabbycat-db-1 psql -U tabbycat tabbycat < backup-20250105.sql
```

### Automate Backups

Add a cron job:
```bash
0 2 * * * docker exec tabbycat-db-1 pg_dump -U tabbycat tabbycat > /backups/tabbycat-$(date +\%Y\%m\%d).sql
```

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.dokploy.yml logs -f

# Specific service
docker-compose -f docker-compose.dokploy.yml logs -f web
```

### Service Status

```bash
docker-compose -f docker-compose.dokploy.yml ps
```

## Troubleshooting

### Database won't connect?
```bash
docker-compose -f docker-compose.dokploy.yml logs db
```

### Static files not loading?
```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.dokploy.yml restart nginx
```

### Reset admin password?
```bash
docker-compose -f docker-compose.dokploy.yml exec web python manage.py changepassword admin
```

## Updating

### Update Application

1. Push changes to Git
2. In Dokploy, click "Redeploy"
3. Monitor deployment logs

### Update Services

```bash
# Pull latest images
docker-compose -f docker-compose.dokploy.yml pull

# Restart with new images
docker-compose -f docker-compose.dokploy.yml up -d
```

## Cost Comparison

| Platform | Monthly Cost | Control |
|----------|--------------|---------|
| Heroku | $25-100+ | Limited |
| Render | $7-50+ | Limited |
| **Dokploy** | **$5-20** | **Full** |

*Dokploy cost = VPS hosting only (e.g., DigitalOcean, Hetzner)*

## Support & Documentation

- 📖 [Full Deployment Guide](./DOKPLOY_DEPLOYMENT.md)
- 🐛 [Tabbycat Issues](https://github.com/TabbycatDebate/tabbycat/issues)
- 💬 [Dokploy Docs](https://docs.dokploy.com)

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│           Internet Traffic              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         Nginx (Port 80/443)              │
│  - Reverse Proxy                         │
│  - Static Files                          │
│  - SSL Termination                       │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│    Django Web (Port 8000)                │
│  - Gunicorn WSGI Server                  │
│  - Tabbycat Application                  │
└───┬──────────────────────┬───────────────┘
    │                      │
    ▼                      ▼
┌─────────────┐      ┌──────────────────┐
│ PostgreSQL  │      │  Background      │
│  Database   │      │   Worker         │
│             │      │  - Channels      │
└─────────────┘      │  - Tasks         │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   Redis Cache    │
                     │  - Sessions      │
                     │  - Channels      │
                     └──────────────────┘
```

## Security Checklist

- [x] Use strong SECRET_KEY (50+ characters)
- [x] Set DEBUG=0 in production
- [x] Use strong database password
- [x] Enable SSL/HTTPS via Dokploy
- [x] Restrict ALLOWED_HOSTS to actual domains
- [x] Regular database backups
- [x] Keep Docker images updated

---

**Ready to deploy?** Run `./deploy-dokploy.sh` or check [DOKPLOY_DEPLOYMENT.md](./DOKPLOY_DEPLOYMENT.md) for detailed instructions!
