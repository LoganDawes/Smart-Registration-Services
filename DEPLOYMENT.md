# Deployment Guide

This guide provides step-by-step instructions for deploying the Smart Registration Services system to various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Static Files](#static-files)
8. [WebSocket Configuration](#websocket-configuration)
9. [Background Tasks](#background-tasks)
10. [Monitoring & Logging](#monitoring--logging)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.11 or higher
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+
- 2GB RAM minimum (4GB recommended for production)
- 10GB disk space

### Required Software

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3-pip python3-venv
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install redis-server
sudo apt-get install nginx  # For production

# macOS (using Homebrew)
brew install python@3.11
brew install postgresql@15
brew install redis
brew install nginx  # For production
```

## Development Deployment

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/LoganDawes/Smart-Registration-Services.git
cd Smart-Registration-Services
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and set USE_SQLITE=True for development
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Populate sample data (optional):**
```bash
python manage.py create_large_sample_data --clear
```

8. **Run development server:**
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## Production Deployment

### Step 1: Server Setup

1. **Update system:**
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

2. **Install dependencies:**
```bash
sudo apt-get install python3.11 python3-pip python3-venv
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install redis-server
sudo apt-get install nginx
sudo apt-get install supervisor  # For process management
```

### Step 2: Database Setup

1. **Create PostgreSQL database:**
```bash
sudo -u postgres psql
CREATE DATABASE smart_registration;
CREATE USER smart_reg_user WITH PASSWORD 'your_secure_password';
ALTER ROLE smart_reg_user SET client_encoding TO 'utf8';
ALTER ROLE smart_reg_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE smart_reg_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smart_registration TO smart_reg_user;
\q
```

### Step 3: Application Setup

1. **Clone repository:**
```bash
cd /opt
sudo git clone https://github.com/LoganDawes/Smart-Registration-Services.git
sudo chown -R $USER:$USER Smart-Registration-Services
cd Smart-Registration-Services
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

4. **Configure environment:**
```bash
cp .env.example .env
nano .env
```

Edit `.env` with production settings:
```env
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
USE_SQLITE=False
DB_NAME=smart_registration
DB_USER=smart_reg_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CAS_SERVER_URL=https://your-cas-server.edu/cas/
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

### Step 4: Gunicorn Setup

1. **Create Gunicorn configuration:**
```bash
sudo nano /etc/systemd/system/smart_registration.service
```

```ini
[Unit]
Description=Smart Registration Services Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/Smart-Registration-Services
Environment="PATH=/opt/Smart-Registration-Services/venv/bin"
EnvironmentFile=/opt/Smart-Registration-Services/.env
ExecStart=/opt/Smart-Registration-Services/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/Smart-Registration-Services/smart_registration.sock \
    smart_registration.wsgi:application

[Install]
WantedBy=multi-user.target
```

2. **Start Gunicorn:**
```bash
sudo systemctl start smart_registration
sudo systemctl enable smart_registration
sudo systemctl status smart_registration
```

### Step 5: Nginx Configuration

1. **Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/smart_registration
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /opt/Smart-Registration-Services/staticfiles/;
    }
    
    location /media/ {
        alias /opt/Smart-Registration-Services/media/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/Smart-Registration-Services/smart_registration.sock;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://unix:/opt/Smart-Registration-Services/smart_registration.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

2. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/smart_registration /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL/HTTPS Setup (with Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Step 7: Celery Setup

1. **Create Celery worker service:**
```bash
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Smart Registration Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/Smart-Registration-Services
Environment="PATH=/opt/Smart-Registration-Services/venv/bin"
EnvironmentFile=/opt/Smart-Registration-Services/.env
ExecStart=/opt/Smart-Registration-Services/venv/bin/celery -A smart_registration worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

2. **Create Celery beat service:**
```bash
sudo nano /etc/systemd/system/celerybeat.service
```

```ini
[Unit]
Description=Smart Registration Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/Smart-Registration-Services
Environment="PATH=/opt/Smart-Registration-Services/venv/bin"
EnvironmentFile=/opt/Smart-Registration-Services/.env
ExecStart=/opt/Smart-Registration-Services/venv/bin/celery -A smart_registration beat --loglevel=info

[Install]
WantedBy=multi-user.target
```

3. **Start Celery services:**
```bash
sudo systemctl start celery celerybeat
sudo systemctl enable celery celerybeat
```

## Docker Deployment

### Using Docker Compose

1. **Clone repository:**
```bash
git clone https://github.com/LoganDawes/Smart-Registration-Services.git
cd Smart-Registration-Services
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Build and start services:**
```bash
docker-compose up -d
```

4. **Create superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Access the application:**
- Application: http://localhost:8000
- Admin: http://localhost:8000/admin

### Docker Services

The docker-compose setup includes:
- **web**: Django application
- **db**: PostgreSQL database
- **redis**: Redis cache/message broker
- **celery**: Celery worker for background tasks
- **celery-beat**: Celery beat scheduler

## Environment Configuration

### Critical Settings

| Variable | Description | Production Value |
|----------|-------------|------------------|
| DEBUG | Debug mode | False |
| SECRET_KEY | Django secret key | Long random string |
| ALLOWED_HOSTS | Allowed hostnames | your-domain.com |
| USE_SQLITE | Use SQLite instead of PostgreSQL | False |
| DB_* | Database credentials | Production values |
| REDIS_HOST | Redis hostname | localhost or container name |
| CAS_SERVER_URL | CAS authentication server | Your CAS server URL |
| SECURE_SSL_REDIRECT | Force HTTPS | True |
| SESSION_COOKIE_SECURE | Secure session cookies | True |
| CSRF_COOKIE_SECURE | Secure CSRF cookies | True |

## Static Files

### Development
```bash
python manage.py collectstatic
```

### Production
Static files are served by Nginx from `/staticfiles/` directory.

## WebSocket Configuration

For WebSocket support in production:

1. Use Daphne (ASGI server) instead of Gunicorn:
```bash
pip install daphne
daphne -b 0.0.0.0 -p 8001 smart_registration.asgi:application
```

2. Update Nginx to proxy WebSocket connections to Daphne.

## Background Tasks

### Starting Celery

Development:
```bash
celery -A smart_registration worker -l info
celery -A smart_registration beat -l info
```

Production: Use systemd services (see Step 7 above).

## Monitoring & Logging

### Log Files

- Application logs: `/opt/Smart-Registration-Services/logs/django.log`
- Nginx access: `/var/log/nginx/access.log`
- Nginx error: `/var/log/nginx/error.log`
- Celery: Check systemd journal with `journalctl -u celery`

### Monitoring Tools

Consider using:
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation
- **New Relic** or **DataDog** for APM

## Troubleshooting

### Server won't start
```bash
python manage.py check --deploy
```

### Database connection errors
```bash
# Test PostgreSQL connection
psql -h localhost -U smart_reg_user -d smart_registration
```

### Static files not loading
```bash
python manage.py collectstatic --clear
sudo systemctl restart smart_registration
```

### WebSocket connections failing
- Check Redis is running: `redis-cli ping`
- Verify CHANNEL_LAYERS configuration
- Check firewall allows WebSocket connections

### Performance issues
- Increase Gunicorn workers
- Enable database connection pooling
- Configure Redis for caching
- Use CDN for static files

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY set
- [ ] HTTPS enabled and forced
- [ ] Secure cookie flags enabled
- [ ] Database credentials secured
- [ ] Firewall configured (allow only 80, 443, 22)
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] CAS authentication properly configured

## Backup Strategy

### Database Backup
```bash
# Create backup
pg_dump -U smart_reg_user smart_registration > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U smart_reg_user smart_registration < backup_20241202.sql
```

### Automated Backups
Add to crontab:
```bash
0 2 * * * pg_dump -U smart_reg_user smart_registration > /backups/db_$(date +\%Y\%m\%d).sql
```

## Support

For deployment issues:
1. Check logs: `tail -f logs/django.log`
2. Review system status: `sudo systemctl status smart_registration`
3. Test configuration: `python manage.py check --deploy`
4. Open an issue on GitHub

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)
