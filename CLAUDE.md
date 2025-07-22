# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage html

# Type checking
mypy core
```

### Code Quality
```bash
# Lint and format code
ruff check .
ruff format .

# Django template linting
djlint --check .
```

### Django Development
```bash
# Run development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Celery (Background Tasks)
```bash
# Start Celery worker
celery -A config.celery_app worker -l info

# Start Celery beat scheduler
celery -A config.celery_app beat

# Monitor with Flower
celery -A config.celery_app flower
```

### Docker Development
```bash
# Local development with Docker
docker-compose -f docker-compose.local.yml up

# Build containers
docker-compose -f docker-compose.local.yml build

# Production deployment
docker-compose -f docker-compose.production.yml up
```

## Project Architecture

This is a Django REST API backend for "Tani Pintar" (Smart Farmer), an agricultural platform connecting farmers, distributors, consumers, suppliers, agents, and vendors.

### Key Applications
- `accounts/` - User profiles, verification codes, location data
- `social_media/` - Posts, images, likes, views, social features
- `thinkflow/` - AI plant disease detection using OpenAI
- `location/` - Country/city geographical data
- `core/users/` - Custom user model and authentication
- `ecommerce/`, `tani/`, `vendors/` - E-commerce related features

### API Structure
- DRF with JWT authentication (`rest_framework_simplejwt`)
- API documentation with `drf-spectacular` (Swagger/OpenAPI)
- CORS enabled for frontend integration
- Redis for caching and Celery message broker
- PostgreSQL database

### Authentication & Profiles
- Custom User model in `core.users`
- Profile types: Farmer, Distributor, Consumer, Supplier, Agent, Vendor
- ID card verification system with status tracking
- Email verification required for registration

### Key Features
- Social media posts with images, likes, and view tracking
- Background task processing with Celery
- Plant disease detection API integration (OpenAI)
- Multi-user type support with role-based functionality
- Location-based services (countries/cities)

### Settings Structure
- `config/settings/base.py` - Base configuration
- `config/settings/local.py` - Local development
- `config/settings/production.py` - Production settings
- Environment variables managed via django-environ

### Testing
- Pytest configuration in `pyproject.toml`
- Factory Boy for test data generation
- Django coverage plugin for accurate coverage reporting
- Test settings in `config.settings.test`