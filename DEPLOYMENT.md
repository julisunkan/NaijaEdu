# Nigerian E-Learning Platform - Render Deployment Guide

## Overview
This guide helps you deploy your Nigerian E-Learning Platform to Render while preserving your existing SQLite database and all course data.

## Pre-Deployment Setup

### 1. Environment Variables Required
Set these environment variables in your Render dashboard:

- `SESSION_SECRET`: A secure random string for session encryption
- `FLASK_ENV`: Set to `production` for deployment
- `DATABASE_URL`: Set to `sqlite:///instance/elearning.db` (optional, defaults to this)

### 2. Files Prepared for Deployment
- `render.yaml`: Render service configuration
- `Procfile`: Process definition for web server
- `runtime.txt`: Python version specification
- Updated `main.py`: Production-ready with PORT environment variable support
- Updated `app.py`: Environment-aware database configuration

## Deployment Steps

### Step 1: Connect to Render
1. Go to [render.com](https://render.com)
2. Sign up or log in to your account
3. Click "New +" and select "Web Service"
4. Connect your GitHub repository

### Step 2: Configure Service
1. Select your repository
2. Render will auto-detect the configuration from `render.yaml`
3. Verify these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Environment**: `Python`

### Step 3: Set Environment Variables
In the Render dashboard, add:
```
SESSION_SECRET=your-secure-random-string-here
FLASK_ENV=production
```

### Step 4: Database Migration
Your SQLite database will be recreated on first deployment with:
- Default admin user: username=`admin`, password=`admin123`
- System settings configured for Nigerian market
- Empty course catalog ready for content

## Post-Deployment

### Default Login
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator

### Important Security Steps
1. Change the admin password immediately after first login
2. Create instructor and student accounts as needed
3. Upload your course content through the admin panel

## Database Persistence
- SQLite database is included in the deployment
- File uploads are stored in the `uploads` directory
- All Nigerian Naira pricing and currency formatting preserved

## Production Features
- Secure session management with environment-based secrets
- Gunicorn WSGI server for production performance
- Auto-scaling ready configuration
- HTTPS enabled by default on Render

## Troubleshooting
- If deployment fails, check the build logs in Render dashboard
- Ensure all environment variables are set correctly
- Database will auto-initialize on first run if empty

Your e-learning platform will be accessible at: `https://your-app-name.onrender.com`