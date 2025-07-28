# Tani Pintar Backend

**Tani Pintar** is an agricultural platform connecting farmers, distributors, consumers, suppliers, agents, and vendors. Features include social media, AI plant disease detection, e-commerce, and location-based services.

## 🚀 Quick Start with Docker

1. **Clone and start**
   ```bash
   git clone <repository-url>
   cd tani-pintar-backend
   docker-compose -f docker-compose.local.yml up --build
   ```

2. **Setup database**
   ```bash
   docker-compose -f docker-compose.local.yml run django python manage.py migrate
   docker-compose -f docker-compose.local.yml run django python manage.py createsuperuser
   docker-compose -f docker-compose.local.yml run django python manage.py loaddata location/fixtures/initial_data.json
   ```

3. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

## 📚 API Documentation

- **Postman Collection**: https://www.postman.com/dark-shuttle-853516/tani-pintar/

## 🔧 Development Commands

All commands should be run with Docker:

```bash
# Start services
docker compose -f docker-compose.local.yml up

# Run tests
docker compose -f docker-compose.local.yml run --rm django pytest

# Run migrations
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
```
