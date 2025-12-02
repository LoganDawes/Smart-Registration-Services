# Contributing to Smart Registration Services

Thank you for your interest in contributing to Smart Registration Services! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Coding Standards](#coding-standards)
6. [Making Changes](#making-changes)
7. [Testing](#testing)
8. [Submitting Changes](#submitting-changes)
9. [Reporting Bugs](#reporting-bugs)
10. [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+
- Git

### Setup Steps

1. **Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/Smart-Registration-Services.git
cd Smart-Registration-Services
```

2. **Add upstream remote:**
```bash
git remote add upstream https://github.com/LoganDawes/Smart-Registration-Services.git
```

3. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your local settings
export USE_SQLITE=True  # For development
```

6. **Run migrations:**
```bash
python manage.py migrate
```

7. **Create superuser:**
```bash
python manage.py createsuperuser
```

8. **Load sample data:**
```bash
python manage.py populate_sample_data
```

9. **Run development server:**
```bash
python manage.py runserver
```

## Project Structure

```
Smart-Registration-Services/
├── advisor/                    # Advisor collaboration module
│   ├── models.py              # Advisor, chat, and comment models
│   ├── views.py               # Advisor views
│   ├── consumers.py           # WebSocket consumers
│   └── routing.py             # WebSocket routing
├── ai_recommendations/         # AI recommendation module
│   ├── models.py              # Recommendation models
│   └── views.py               # Recommendation views
├── authentication/             # User authentication module
│   ├── models.py              # Custom user model
│   ├── views.py               # Authentication views
│   └── admin.py               # User admin interface
├── courses/                    # Course catalog module
│   ├── models.py              # Course and section models
│   ├── views.py               # Course API views
│   ├── serializers.py         # DRF serializers
│   └── management/            # Management commands
├── infrastructure/             # Infrastructure and monitoring
│   ├── models.py              # Logging and metrics models
│   └── views.py               # Infrastructure views
├── notifications/              # Notification module
│   ├── models.py              # Notification models
│   ├── tasks.py               # Celery tasks
│   └── views.py               # Notification views
├── planning/                   # Student planning module
│   ├── models.py              # Plan and conflict models
│   └── views.py               # Planning views
├── registration/               # Registration module
│   ├── models.py              # Enrollment and request models
│   └── views.py               # Registration views
├── smart_registration/         # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configuration
│   ├── asgi.py                # ASGI configuration
│   └── celery.py              # Celery configuration
├── templates/                  # HTML templates
├── static/                     # Static files (CSS, JS, images)
├── requirements.txt            # Python dependencies
├── manage.py                  # Django management script
├── docker-compose.yml         # Docker configuration
└── README.md                  # Project documentation
```

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines and use these tools:

```bash
# Format code with Black
black .

# Check code with flake8
flake8 .
```

### Key Conventions

1. **Naming:**
   - Use `snake_case` for functions and variables
   - Use `PascalCase` for class names
   - Use `UPPER_CASE` for constants

2. **Imports:**
   - Standard library imports first
   - Third-party imports second
   - Local imports last
   - Alphabetical order within each group

3. **Docstrings:**
   - Use docstrings for all modules, classes, and functions
   - Follow Google docstring format

Example:
```python
def calculate_total_credits(courses):
    """
    Calculate total credits for a list of courses.
    
    Args:
        courses (list): List of Course objects
        
    Returns:
        int: Total number of credits
    """
    return sum(course.credits for course in courses)
```

4. **Type Hints:**
   - Use type hints for function parameters and return values
   
```python
def get_student_plan(student_id: int) -> Optional[StudentPlan]:
    """Get student plan by ID."""
    return StudentPlan.objects.filter(student_id=student_id).first()
```

### Django Best Practices

1. **Models:**
   - Use descriptive field names
   - Add `help_text` for clarity
   - Include `verbose_name` and `verbose_name_plural`
   - Use `related_name` for foreign keys
   - Add `__str__` method for readable representation

2. **Views:**
   - Use class-based views when appropriate
   - Keep views thin, move logic to models or services
   - Use proper HTTP methods (GET, POST, PUT, DELETE)

3. **Serializers:**
   - Validate input data
   - Use appropriate read-only fields
   - Add custom validation methods when needed

4. **URLs:**
   - Use descriptive URL patterns
   - Use URL namespacing
   - Follow REST conventions for API endpoints

### Database

1. **Migrations:**
   - Create migrations for all model changes
   - Review migrations before committing
   - Use descriptive migration names

```bash
python manage.py makemigrations --name add_student_major_field
```

2. **Queries:**
   - Use `select_related()` and `prefetch_related()` to avoid N+1 queries
   - Use database indexes for frequently queried fields
   - Avoid query loops

### Testing

1. **Write tests for:**
   - All models
   - All views and API endpoints
   - All utility functions
   - Edge cases and error conditions

2. **Test structure:**
```python
from django.test import TestCase
from authentication.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            role=User.Role.STUDENT
        )
    
    def test_user_creation(self):
        """Test user is created correctly."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.is_student())
    
    def test_user_string_representation(self):
        """Test user string representation."""
        self.assertIn('testuser', str(self.user))
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/course-search-filters`
- `bugfix/enrollment-validation`
- `docs/api-documentation`
- `refactor/optimize-queries`

### Commit Messages

Write clear, descriptive commit messages:

```
Add course conflict detection algorithm

- Implement time overlap detection
- Add prerequisite validation
- Include unit tests
- Update documentation

Fixes #123
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description if needed
- Reference issue numbers

### Development Workflow

1. **Update your local main:**
```bash
git checkout main
git pull upstream main
```

2. **Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

3. **Make changes:**
   - Write code
   - Add tests
   - Update documentation

4. **Test changes:**
```bash
python manage.py test
python manage.py check
```

5. **Commit changes:**
```bash
git add .
git commit -m "Your descriptive commit message"
```

6. **Push to your fork:**
```bash
git push origin feature/your-feature-name
```

7. **Create pull request:**
   - Go to GitHub
   - Click "New Pull Request"
   - Provide clear description
   - Link related issues

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test courses

# Run specific test class
python manage.py test courses.tests.CourseModelTest

# Run with verbosity
python manage.py test --verbosity=2
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Writing Tests

Each app should have a `tests.py` file (or `tests/` directory) with:
- Model tests
- View tests
- API tests
- Integration tests

## Submitting Changes

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Changes are focused and minimal

### Pull Request Description

Include in your PR description:
- What the changes do
- Why the changes are needed
- How to test the changes
- Related issues (use "Fixes #123", "Closes #456")
- Screenshots (for UI changes)

### Review Process

1. Automated checks will run (tests, linting)
2. Project maintainers will review
3. Address review comments
4. Once approved, PR will be merged

## Reporting Bugs

### Before Reporting

1. Check if bug already reported
2. Try to reproduce with latest version
3. Gather relevant information

### Bug Report Template

```markdown
**Description**
A clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- Django version: [e.g., 4.2]
- Browser: [if applicable]

**Additional Context**
Screenshots, error logs, etc.
```

## Feature Requests

### Suggesting Features

1. Check if feature already suggested
2. Explain the use case
3. Describe the solution
4. Consider alternatives

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
A clear description of what you want

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Mockups, examples, etc.
```

## Questions?

- Check the [README](README.md)
- Check the [API Documentation](API.md)
- Check existing issues
- Ask in discussions
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Smart Registration Services!
