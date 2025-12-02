# Smart Registration Services

A comprehensive university course-planning and registration system built with Django, designed to support students, advisors, and registrar staff through an integrated, modular architecture.

## 🎯 Overview

Smart Registration Services is a modern web application that streamlines the course registration process at universities. The system provides:

- **Students**: Course search, schedule planning, conflict detection, and registration workflows
- **Advisors**: Student plan review, real-time chat, approval workflows, and collaboration tools
- **Registrar**: Course management, enrollment tracking, and system administration

## 🏗️ Architecture

The system is built as eight independent but integrated modules:

### 1. Authentication & User Management
- CAS authentication integration
- Role-based access control (Student, Advisor, Registrar)
- User session management and permissions

### 2. Course Catalog & Search Engine
- Comprehensive course database with prerequisites
- Advanced search, filtering, and sorting capabilities
- RESTful API endpoints for course data

### 3. Student Planning & Schedule Visualization
- Interactive schedule builder
- Automatic conflict detection
- Visual weekly schedule views
- Advisor comment integration

### 4. Registration & Enrollment Processing
- Add/drop course functionality
- Mandatory advisor approval workflows
- Concurrent enrollment handling
- Registration audit logging

### 5. Advisor Collaboration & Messaging
- Real-time WebSocket chat system
- Plan review dashboard
- Comment and annotation tools
- Approval/rejection workflows

### 6. AI Recommendation & Degree-Planning
- Personalized course recommendations
- Degree requirement tracking
- AI-powered schedule optimization
- Learning from approval patterns

### 7. Notification & Event Trigger
- Email and push notifications
- Celery-based asynchronous delivery
- Event-driven notification triggers
- User notification preferences

### 8. Infrastructure, Performance & Data Pipeline
- System monitoring and logging
- API performance metrics
- Error handling and security
- Registrar data import pipelines

## 🚀 Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Real-Time**: Django Channels + Redis (WebSockets)
- **Background Tasks**: Celery + Redis
- **Frontend**: Django Templates + HTMX + Tailwind CSS
- **Authentication**: django-cas-ng
- **API Documentation**: drf-spectacular (Swagger/ReDoc)
- **Containerization**: Docker + Docker Compose

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+
- Docker & Docker Compose (optional but recommended)

## 🔧 Installation & Setup

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

## 🗄️ Database Models

### Authentication Models
- **User**: Custom user model with role-based permissions (Student, Advisor, Registrar)

### Course Models
- **Course**: Course catalog entries with prerequisites
- **CourseSection**: Specific course sections with schedules and enrollment limits

### Planning Models
- **StudentPlan**: Student course plans with approval workflows
- **PlannedCourse**: Individual courses in a student's plan
- **ScheduleConflict**: Detected schedule conflicts

### Registration Models
- **Enrollment**: Student enrollments in course sections
- **RegistrationRequest**: Registration requests requiring advisor approval
- **RegistrationLog**: Audit log for all registration actions

### Advisor Models
- **AdvisorAssignment**: Student-advisor relationships
- **ChatMessage**: Real-time chat messages
- **PlanComment**: Advisor comments on student plans

### AI Models
- **DegreeRequirement**: Degree program requirements
- **CourseRecommendation**: AI-generated course recommendations
- **RecommendationFeedback**: User feedback for learning

### Notification Models
- **Notification**: System notifications
- **NotificationPreference**: User notification preferences

### Infrastructure Models
- **SystemLog**: System-wide logging
- **APIMetrics**: API performance tracking

## 🔑 API Endpoints

### Course Catalog
- `GET /api/courses/` - List all courses
- `GET /api/courses/{id}/` - Course details
- `GET /api/sections/` - List course sections
- `GET /api/sections/{id}/` - Section details
- `GET /api/sections/available/` - Sections with available seats

### Authentication
- `GET/POST /accounts/login/` - CAS login
- `GET /accounts/logout/` - CAS logout

### Documentation
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## 🔐 Security Features

- CAS authentication integration
- Role-based access control
- HTTPS/SSL support (configurable)
- Secure session cookies
- CSRF protection
- XSS protection headers
- SQL injection prevention (Django ORM)
- Input validation and sanitization

## 📊 Admin Interface

The Django admin interface provides comprehensive management tools:

- User management with role assignment
- Course and section management
- Enrollment and registration tracking
- Notification management
- System logs and metrics

Access at: http://localhost:8000/admin/

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## 📈 Monitoring & Logging

Logs are stored in the `logs/` directory:
- `django.log` - Application logs

Database logging tracks:
- System events and errors
- API performance metrics
- Registration actions
- User activities

## 🚢 Deployment

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Team

Smart Registration Services Team

## 📧 Support

For support, please open an issue on the GitHub repository.

## 🗺️ Roadmap

### Phase 1: Core Infrastructure (Completed)
- ✅ Project setup and configuration
- ✅ Database models and migrations
- ✅ Authentication and user management
- ✅ Basic API endpoints

### Phase 2: Course Management (In Progress)
- ✅ Course catalog API
- ⏳ Course search and filtering
- ⏳ Section management
- ⏳ Prerequisites handling

### Phase 3: Planning & Registration
- ⏳ Schedule builder interface
- ⏳ Conflict detection
- ⏳ Registration workflows
- ⏳ Advisor approval system

### Phase 4: Collaboration & Communication
- ⏳ WebSocket chat implementation
- ⏳ Advisor dashboard
- ⏳ Plan review interface
- ⏳ Notification system

### Phase 5: AI & Recommendations
- ⏳ Recommendation engine
- ⏳ Degree planning
- ⏳ Learning from feedback

### Phase 6: Production Readiness
- ⏳ Performance optimization
- ⏳ Security hardening
- ⏳ Comprehensive testing
- ⏳ Documentation completion

## 🔗 Related Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [HTMX Documentation](https://htmx.org/docs/)

