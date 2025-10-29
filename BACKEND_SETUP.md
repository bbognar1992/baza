# Pontum Backend Setup Guide

This guide will help you set up and run the Pontum Construction Management System backend API.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- PostgreSQL database (or use the provided Docker setup)

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Start the backend with Docker:**
   ```bash
   ./run_backend.sh docker
   ```

2. **Or use Docker Compose:**
   ```bash
   ./run_backend.sh compose
   ```

### Option 2: Local Development

1. **Start the backend locally:**
   ```bash
   ./run_backend.sh local
   ```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/baza_db

# SQLAlchemy Configuration
SQLALCHEMY_ECHO=false

# SSL Configuration (optional)
SSL_MODE=require
SSL_CERT_PATH=
SSL_KEY_PATH=
SSL_CA_PATH=

# Backend Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

## Available Commands

The `run_backend.sh` script provides several commands:

```bash
# Start backend with Docker
./run_backend.sh docker

# Start backend with Docker Compose
./run_backend.sh compose

# Start backend locally (development)
./run_backend.sh local

# Stop backend services
./run_backend.sh stop

# Show backend logs
./run_backend.sh logs

# Check backend status
./run_backend.sh status

# Test API endpoints
./run_backend.sh test

# Show help
./run_backend.sh help
```

## API Documentation

Once the backend is running, you can access:

- **API Base URL:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## Available Endpoints

The API includes the following endpoint groups:

- **Users:** `/api/v1/users`
- **Projects:** `/api/v1/projects`
- **Resources:** `/api/v1/resources`
- **Materials:** `/api/v1/materials`
- **Tasks:** `/api/v1/tasks`
- **Phases:** `/api/v1/phases`
- **Profession Types:** `/api/v1/profession-types`
- **Project Types:** `/api/v1/project-types`
- **Weather:** `/api/v1/weather`

## Database Setup

The backend uses PostgreSQL. Make sure you have:

1. PostgreSQL running locally, OR
2. A cloud database (like Supabase), OR
3. Use Docker to run PostgreSQL

### Using Docker for PostgreSQL

```bash
# Start PostgreSQL with Docker
docker run --name baza-postgres \
  -e POSTGRES_DB=baza_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use:**
   ```bash
   # Find and kill the process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database connection issues:**
   - Check your DATABASE_URL in the .env file
   - Ensure PostgreSQL is running
   - Verify database credentials

3. **Docker issues:**
   ```bash
   # Clean up Docker containers
   docker system prune -a
   
   # Rebuild the image
   docker build -t baza-backend ./backend
   ```

4. **Missing dependencies:**
   ```bash
   # Install Python dependencies locally
   cd backend
   pip install -r requirements.txt
   ```

### Checking Status

```bash
# Check if backend is running
./run_backend.sh status

# Test API endpoints
./run_backend.sh test

# View logs
./run_backend.sh logs
```

## Development

For development, use the local option:

```bash
./run_backend.sh local
```

This will:
- Create a virtual environment
- Install dependencies
- Start the server with auto-reload
- Enable debugging

## Production Deployment

For production deployment:

1. Use the Docker approach
2. Set up proper environment variables
3. Configure SSL/TLS
4. Set up monitoring and logging
5. Use a production database

## Support

If you encounter issues:

1. Check the logs: `./run_backend.sh logs`
2. Test the API: `./run_backend.sh test`
3. Check the status: `./run_backend.sh status`
4. Review the API documentation at http://localhost:8000/docs

