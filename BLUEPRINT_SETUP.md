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

## Email Configuration (Optional but Recommended)

### 📧 **EMAIL_HOST**
- **What it is**: SMTP server for sending emails
- **Example**: `smtp.gmail.com`, `smtp.outlook.com`, `smtp.yahoo.com`
- **Used for**: Sending notifications, password resets, etc.

### 🔌 **EMAIL_PORT**
- **What it is**: SMTP server port
- **Example**: `587` (TLS), `465` (SSL), `25` (unsecured)
- **Most common**: `587`

### 👤 **EMAIL_HOST_USER**
- **What it is**: Email account username
- **Example**: `tournament@yourdomain.com`, `tabdirector@gmail.com`
- **Note**: Use a dedicated email account for the tournament

### 🔑 **EMAIL_HOST_PASSWORD**
- **What it is**: Email account password or app-specific password
- **For Gmail**: Use an [App Password](https://support.google.com/accounts/answer/185833)
- **Security**: Never use your personal password

### 🔐 **EMAIL_USE_TLS**
- **What it is**: Use encrypted connection
- **Example**: `True` (recommended), `False`
- **Default**: `True`

### 📬 **DEFAULT_FROM_EMAIL**
- **What it is**: Email address shown as sender
- **Example**: `noreply@tournament.com`, `WUDC 2025 <notifications@wudc.org>`
- **Used for**: All automated emails from the system

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

Email Configuration:
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_HOST_USER: notifications@oxfordiv.com
EMAIL_HOST_PASSWORD: your-app-specific-password
EMAIL_USE_TLS: True
DEFAULT_FROM_EMAIL: Oxford IV 2025 <noreply@oxfordiv.com>

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