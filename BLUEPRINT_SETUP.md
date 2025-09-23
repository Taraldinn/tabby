# Tabbycat Blueprint Setup Guide

When you deploy this Tabbycat blueprint on Render, you'll be prompted to provide the following information:

## Required Configuration

### 📧 **TAB_DIRECTOR_EMAIL**
- **What it is**: Your email address as the tournament director
- **Example**: `director@mytournament.com`
- **Used for**: Admin notifications, system emails, and contact information

### 🌍 **TIME_ZONE**
- **What it is**: The timezone for your tournament
- **Example**: `Asia/Dhaka`, `America/New_York`, `Europe/London`
- **Format**: Use [IANA timezone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- **Used for**: Displaying correct local times for rounds, deadlines, etc.

### 🏆 **TOURNAMENT_NAME**
- **What it is**: The official name of your tournament
- **Example**: `World Universities Debating Championship 2025`
- **Used for**: Page titles, emails, and tournament branding

### 🌐 **SITE_NAME**
- **What it is**: Short name for your tournament site
- **Example**: `WUDC 2025`, `Oxford IV`, `Cambridge Open`
- **Used for**: Browser tab titles and navigation

## Service Names (Customizable)

You can customize the service names during blueprint setup:

- **Main Web Service**: `tabio` → Change to your tournament name (e.g., `wudc2025`)
- **Worker Service**: `tabio_worker` → Will become `yourname_worker`
- **Database**: `tabio_db` → Will become `yourname_db`
- **Redis**: `tabio_redis` → Will become `yourname_redis`

## Example Configuration

For a tournament called "Oxford IV 2025":

```
TAB_DIRECTOR_EMAIL: director@oxfordiv.com
TIME_ZONE: Europe/London
TOURNAMENT_NAME: Oxford IV 2025
SITE_NAME: Oxford IV
Service prefix: oxfordiv (changes tabio → oxfordiv)
```

This will create:
- Website URL: `oxfordiv-xxxxx.onrender.com`
- Services: `oxfordiv`, `oxfordiv_worker`, `oxfordiv_db`, `oxfordiv_redis`

## Deployment Steps

1. **Click "Deploy to Render"** or use Blueprint in Render Dashboard
2. **Fill in the configuration values** above
3. **Customize service names** (optional)
4. **Click "Apply"** to start deployment
5. **Wait for all services** to build and start
6. **Access your tournament** at the provided URL

## After Deployment

1. **Create admin account**: Access your site and create the first admin user
2. **Configure tournament settings**: Set up your tournament parameters
3. **Import data**: Add institutions, teams, adjudicators, and venues
4. **Start your tournament**: Begin registration and draw management

All services will be automatically configured and connected! 🚀