# Tabbycat Blueprint Setup Guide

When you deploy this Tabbycat blueprint on Render, you'll be prompted to provide the following information:

## Prerequisites

### Database Setup

This blueprint requires an external PostgreSQL database. You can use:

1. **Supabase** (Recommended - Free tier available)
   - Go to [supabase.com](https://supabase.com) and create a new project
   - Navigate to **Settings** → **Database**
   - Copy the **Connection string** (URI format)
   - Example: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require`

2. **Other PostgreSQL providers**
   - AWS RDS
   - Digital Ocean Managed Databases
   - ElephantSQL
   - Neon
   - Any PostgreSQL 12+ database

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

### 🗄️ **DATABASE_URL** (Required)
- **What it is**: PostgreSQL database connection string
- **Example**: `postgresql://user:password@host:5432/database?sslmode=require`
- **Options**: 
  - Use Render's internal PostgreSQL (free tier)
  - Use external database (Supabase, AWS RDS, etc.)
- **For Supabase**: 
  - Go to **Settings** → **Database** in your Supabase project
  - Copy the **Connection string** (URI format)
  - **Important**: Make sure it ends with `?sslmode=require`
  - Example: `postgresql://postgres:yourpassword@db.xxxxx.supabase.co:5432/postgres?sslmode=require`
- **IPv6 Note**: The app automatically forces IPv4 connections to work with Render's network
  - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require`

## Service Names (Customizable)

You can customize the service names during blueprint setup:

- **Main Web Service**: `tabio` → Change to your tournament name (e.g., `wudc2025`)
- **Worker Service**: `tabio_worker` → Will become `yourname_worker`
- **Redis**: `tabio_redis` → Will become `yourname_redis`

**Note**: This blueprint uses external database (like Supabase) instead of Render's internal database service.

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
4. **Test email configuration**: Send a test email to verify email settings are working
5. **Start your tournament**: Begin registration and draw management

## Email Configuration Testing

To verify that email sending is working correctly:

1. **Access Django admin**: Go to `/admin/` on your deployed site
2. **Test email**: Use Django's built-in email functionality or create a test view
3. **Check email settings**: Ensure all email environment variables were set during setup:
   - `EMAIL_HOST`: Your SMTP server (e.g., `smtp.gmail.com`)
   - `EMAIL_PORT`: SMTP port (usually `587` for TLS)
   - `EMAIL_HOST_USER`: Your email username
   - `EMAIL_HOST_PASSWORD`: Your email password or app password
   - `EMAIL_USE_TLS`: Set to `true` for secure connections
   - `DEFAULT_FROM_EMAIL`: The default sender email address

## Troubleshooting

### Database Issues
- **"Network is unreachable"**: This is an IPv6 connectivity issue between Render and Supabase
  - ✅ **Already fixed**: The app automatically forces IPv4 connections
  - Ensure your `DATABASE_URL` includes `?sslmode=require`
  - Verify your Supabase database is active (not paused)
- **"No support for ''"**: The `DATABASE_URL` is empty
  - Check that you entered the database URL during blueprint setup
  - Go to Render dashboard → Service → Environment → Add `DATABASE_URL`
- **SSL/TLS errors**: 
  - Ensure `?sslmode=require` is at the end of your `DATABASE_URL`
  - Check Supabase SSL certificate is valid

### Email Issues
- **Connection refused**: Check your SMTP server settings and credentials
- **Authentication failed**: Verify username/password, consider using app passwords for Gmail
- **TLS errors**: Ensure `EMAIL_USE_TLS` is set to `true` for secure SMTP servers

### Service Issues
- **Services not starting**: Check the Render dashboard for build logs and error messages
- **Database connection**: Verify the database service is running and properly connected
- **Redis connection**: Ensure the Redis service is accessible to both web and worker services

All services will be automatically configured and connected! 🚀