# Smart Registration Services

A comprehensive university course-planning and registration system built with Django, designed to support students, advisors, and registrar staff through an integrated, modular architecture.

## Overview

Smart Registration Services is a modern web application that streamlines the course registration process at universities. The system provides Course search, schedule planning, and registration workflows

## Team

Logan Dawes
Shay Philips
Adelyn Jones
Justice Brown
Elijah Yanez
Gannon DeHollander
Charan Teja Uppu
Clayton Nunley

## Architecture

The system is built as eight independent but integrated modules:

### 1. Authentication & User Management
- CAS authentication integration, not yet implemented

### 2. Course Catalog & Search Engine
- Course database with sorting capabilities

### 3. Student Planning & Schedule Visualization
- Visual weekly schedule views

### 4. Registration & Enrollment Processing
- Add/drop course functionality

### 5. Advisor Collaboration & Messaging
- For future implementation

### 6. AI Recommendation & Degree-Planning
- Not fully completed

### 7. Notification & Event Trigger
- Email and push notifications
- Event-driven notification triggers

### 8. Infrastructure, Performance & Data Pipeline
- System monitoring and logging

## Tech Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Real-Time**: Django Channels + Redis (WebSockets)
- **Background Tasks**: Celery + Redis
- **Frontend**: Django Templates + HTMX + Tailwind CSS
- **Authentication**: django-cas-ng
- **API Documentation**: drf-spectacular (Swagger/ReDoc)
- **Containerization**: Docker + Docker Compose

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+
- Docker & Docker Compose (optional but recommended)

## Installation & Setup

### Option 1: Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/LoganDawes/Smart-Registration-Services.git
cd Smart-Registration-Services
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Start all services with Docker Compose:
```bash
docker-compose up -d
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Access the application:
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin
- API documentation: http://localhost:8000/api/docs/

### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/LoganDawes/Smart-Registration-Services.git
cd Smart-Registration-Services
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

8. In separate terminals, start Celery and Redis:
```bash
# Terminal 2: Start Redis
redis-server

# Terminal 3: Start Celery worker
celery -A smart_registration worker -l info

# Terminal 4: Start Celery beat (for scheduled tasks)
celery -A smart_registration beat -l info
```

## Testing

Run tests with:
```bash
python manage.py test
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Monitoring & Logging

Logs are stored in the `logs/` directory:
- `django.log` - Application logs

## Deployment

### Production Checklist

1. Set `DEBUG=False` in `.env`
2. Configure proper `SECRET_KEY`
3. Set `ALLOWED_HOSTS` appropriately
4. Enable HTTPS settings
5. Configure production database
6. Set up email backend
7. Configure CAS server URLs
8. Set up static file serving
9. Configure Redis for production
10. Set up monitoring and logging

### Environment Variables

Key environment variables (see `.env.example` for complete list):

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (False for production)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` - Database configuration
- `REDIS_HOST`, `REDIS_PORT` - Redis configuration
- `CAS_SERVER_URL` - CAS authentication server
- `EMAIL_HOST`, `EMAIL_PORT` - Email configuration