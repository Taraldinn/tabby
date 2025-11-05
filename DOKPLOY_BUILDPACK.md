# Dokploy Buildpack Deployment Guide

This guide covers deploying Tabbycat on Dokploy using **Heroku Buildpacks** (alternative to Docker).

## What are Buildpacks?

Buildpacks are scripts that automatically detect and build your application without needing a Dockerfile. They're easier to use and configure than Docker for standard applications.

## Deployment Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Buildpacks** | Easy setup, auto-detection, fast builds | Less control | Quick deploys, standard apps |
| **Docker** | Full control, reproducible | Complex setup | Custom requirements |
| **Nixpacks** | Fast, declarative | Newer, less docs | Modern deployments |

## Quick Start with Buildpacks

### 1️⃣ Create Application in Dokploy

1. Open Dokploy dashboard
2. Click **"Create Application"**
3. Choose **"Buildpack"** as build method
4. Connect your Git repository
5. Select branch: `master`

### 2️⃣ Configure Buildpacks

Dokploy will auto-detect buildpacks, or you can specify them:

**Option A: Auto-detection** (Recommended)
- Dokploy detects Python and Node.js automatically

**Option B: Manual specification**
Add in Dokploy settings:
```
heroku/nodejs
heroku/python
```

**Option C: Use .buildpacks file**
Already included in this repo at `.buildpacks`

### 3️⃣ Environment Variables

Add these in Dokploy dashboard:

**Required:**
```bash
# Django
SECRET_KEY=<generate-with-command-below>
DJANGO_SETTINGS_MODULE=settings

# Database (auto-provided by Dokploy PostgreSQL addon)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (auto-provided by Dokploy Redis addon)
REDIS_URL=redis://host:6379/0
```

**Optional:**
```bash
# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Site
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=0
DISABLE_SENTRY=1
```

**Generate SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 4️⃣ Add Services

In Dokploy, add these services to your application:

**PostgreSQL:**
- Service: PostgreSQL 15
- Volume: `/var/lib/postgresql/data`
- Auto-generates `DATABASE_URL`

**Redis:**
- Service: Redis 7
- Volume: `/data`
- Auto-generates `REDIS_URL`

### 5️⃣ Deploy

Click **"Deploy"** and wait 2-3 minutes.

## Build Process

When you deploy with buildpacks, Dokploy will:

1. **Detect** - Auto-detect Node.js and Python
2. **Install Node.js** - Install dependencies from `package.json`
3. **Install Python** - Install from `Pipfile` or `requirements.txt`
4. **Build** - Run `npm run build` if configured
5. **Collect Static** - Run `python manage.py collectstatic`
6. **Start** - Launch processes from `Procfile`

## Procfile Configuration

The `Procfile` tells Dokploy which processes to run:

```procfile
web: honcho -f ProcfileMulti start
worker: python manage.py runworker notifications adjallocation venues
```

- **web**: Main application server
- **worker**: Background task processor

## Build Configuration Files

### .buildpacks
Specifies buildpacks in order:
```
https://github.com/heroku/heroku-buildpack-nodejs.git
https://github.com/heroku/heroku-buildpack-python.git
```

### dokploy.toml (Optional)
Advanced configuration:
```toml
[build]
builder = "buildpack"
buildpacks = ["heroku/nodejs", "heroku/python"]

[deploy]
port = 8000

[services.web]
command = "gunicorn wsgi:application --config config/gunicorn.conf"
instances = 1
```

### nixpacks.toml (Alternative)
If using Nixpacks instead of buildpacks:
```toml
[phases.setup]
nixPkgs = ["nodejs-18_x", "python311"]

[start]
cmd = "gunicorn wsgi:application --config config/gunicorn.conf"
```

## Post-Deployment

### Create Superuser

```bash
# Via Dokploy console
dokploy run web python manage.py createsuperuser

# Or via environment variables
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=secure-password
```

### Run Migrations

Migrations run automatically via `Procfile` release phase.

Manual migration:
```bash
dokploy run web python manage.py migrate
```

### Collect Static Files

```bash
dokploy run web python manage.py collectstatic --noinput
```

## Scaling

### Horizontal Scaling

In Dokploy dashboard:
1. Go to application → Processes
2. Adjust instance count:
   - **web**: 1-5 instances (handle more users)
   - **worker**: 1-3 instances (faster background jobs)

### Vertical Scaling

Adjust instance size:
- **Eco**: $5/month (512MB RAM)
- **Basic**: $7/month (1GB RAM)
- **Standard**: $25/month (2.5GB RAM)

## Monitoring

### View Logs

```bash
# All processes
dokploy logs

# Specific process
dokploy logs web
dokploy logs worker
```

### Process Status

```bash
dokploy ps
```

## Troubleshooting

### Build Failures

**Error: "Buildpack detection failed"**
```bash
# Solution: Add .buildpacks file
echo "heroku/nodejs" > .buildpacks
echo "heroku/python" >> .buildpacks
```

**Error: "Failed to install dependencies"**
```bash
# Check Pipfile.lock is up to date
pipenv lock
git commit -am "Update Pipfile.lock"
git push
```

### Runtime Issues

**Database connection error:**
```bash
# Verify DATABASE_URL is set
dokploy config

# Test connection
dokploy run web python manage.py dbshell
```

**Static files not loading:**
```bash
# Re-collect static files
dokploy run web python manage.py collectstatic --noinput --clear
```

**Worker not processing tasks:**
```bash
# Check worker logs
dokploy logs worker

# Restart worker
dokploy restart worker
```

## Environment-Specific Settings

### Development
```bash
DEBUG=1
ALLOWED_HOSTS=*
```

### Staging
```bash
DEBUG=0
ALLOWED_HOSTS=staging.yourdomain.com
```

### Production
```bash
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DISABLE_SENTRY=0  # Enable error tracking
```

## Comparison: Buildpack vs Docker

### Use Buildpacks When:
✅ Standard Python/Node.js app  
✅ Want quick deployment  
✅ Don't need custom system packages  
✅ Prefer simplicity over control  

### Use Docker When:
✅ Need custom system dependencies  
✅ Require specific versions/configurations  
✅ Want reproducible builds  
✅ Complex multi-service setup  

## Advanced Configuration

### Custom Buildpack

Create `.buildpacks`:
```
https://github.com/heroku/heroku-buildpack-apt.git
https://github.com/heroku/heroku-buildpack-nodejs.git
https://github.com/heroku/heroku-buildpack-python.git
```

### Pre/Post Deploy Hooks

Add to `app.json`:
```json
{
  "scripts": {
    "postdeploy": "python manage.py migrate && python manage.py collectstatic --noinput"
  }
}
```

### Build-time Environment Variables

```bash
# In Dokploy, under Build Settings
NODE_ENV=production
PYTHON_VERSION=3.11.4
```

## Migration from Heroku

If migrating from Heroku to Dokploy:

1. **Export Database:**
   ```bash
   heroku pg:backups:capture
   heroku pg:backups:download
   ```

2. **Import to Dokploy:**
   ```bash
   dokploy pg:restore database < latest.dump
   ```

3. **Update Environment Variables:**
   - Copy from Heroku: `heroku config`
   - Add to Dokploy dashboard

4. **Deploy:**
   ```bash
   git push dokploy master
   ```

## Cost Comparison

| Component | Heroku | Dokploy (Buildpack) |
|-----------|--------|---------------------|
| Dyno (web) | $7/mo | $5/mo |
| Dyno (worker) | $7/mo | $5/mo |
| PostgreSQL | $9/mo | $5/mo (VPS included) |
| Redis | $15/mo | $0 (VPS included) |
| **Total** | **$38/mo** | **$15/mo** |

*Dokploy runs on your VPS (e.g., $5/mo DigitalOcean Droplet)*

## Resources

- 📦 [Heroku Buildpacks](https://devcenter.heroku.com/articles/buildpacks)
- 🚀 [Dokploy Docs](https://docs.dokploy.com)
- 🐍 [Python Buildpack](https://github.com/heroku/heroku-buildpack-python)
- 📦 [Node.js Buildpack](https://github.com/heroku/heroku-buildpack-nodejs)

---

**Quick Deploy:** Run `./deploy-dokploy.sh` and choose buildpack deployment option!
