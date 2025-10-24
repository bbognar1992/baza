# ÉpítAI Construction Management API

FastAPI backend server for the ÉpítAI Construction Management System.

## Features

- **Complete CRUD operations** for all models:
  - Users
  - Projects (with locations and members)
  - Resources
  - Materials (with project materials)
  - Tasks (with project tasks and assignments)
  - Phases (with project phases)
  - Profession Types
  - Project Types
  - Weather Data

- **RESTful API** with proper HTTP status codes
- **Pagination** for list endpoints
- **Filtering** and query parameters
- **Data validation** with Pydantic schemas
- **Database integration** with SQLAlchemy
- **CORS support** for frontend integration
- **Auto-generated documentation** at `/docs`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL="your_database_url"
export SQLALCHEMY_ECHO="False"
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user
- `POST /api/v1/users/` - Create user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Projects
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{project_id}` - Get project
- `POST /api/v1/projects/` - Create project
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `GET /api/v1/projects/{project_id}/locations` - Get project locations
- `POST /api/v1/projects/{project_id}/locations` - Add project location
- `GET /api/v1/projects/{project_id}/members` - Get project members
- `POST /api/v1/projects/{project_id}/members` - Add project member

### Resources
- `GET /api/v1/resources/` - List resources
- `GET /api/v1/resources/{resource_id}` - Get resource
- `POST /api/v1/resources/` - Create resource
- `PUT /api/v1/resources/{resource_id}` - Update resource
- `DELETE /api/v1/resources/{resource_id}` - Delete resource

### Materials
- `GET /api/v1/materials/` - List materials
- `GET /api/v1/materials/{material_id}` - Get material
- `POST /api/v1/materials/` - Create material
- `PUT /api/v1/materials/{material_id}` - Update material
- `DELETE /api/v1/materials/{material_id}` - Delete material
- `GET /api/v1/materials/projects/{project_id}/materials` - Get project materials
- `POST /api/v1/materials/projects/{project_id}/materials` - Add project material

### Tasks
- `GET /api/v1/tasks/` - List tasks
- `GET /api/v1/tasks/{task_id}` - Get task
- `POST /api/v1/tasks/` - Create task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task

### Phases
- `GET /api/v1/phases/` - List phases
- `GET /api/v1/phases/{phase_id}` - Get phase
- `POST /api/v1/phases/` - Create phase
- `PUT /api/v1/phases/{phase_id}` - Update phase
- `DELETE /api/v1/phases/{phase_id}` - Delete phase

### Profession Types
- `GET /api/v1/profession-types/` - List profession types
- `GET /api/v1/profession-types/{profession_type_id}` - Get profession type
- `POST /api/v1/profession-types/` - Create profession type
- `PUT /api/v1/profession-types/{profession_type_id}` - Update profession type
- `DELETE /api/v1/profession-types/{profession_type_id}` - Delete profession type

### Project Types
- `GET /api/v1/project-types/` - List project types
- `GET /api/v1/project-types/{project_type_id}` - Get project type
- `POST /api/v1/project-types/` - Create project type
- `PUT /api/v1/project-types/{project_type_id}` - Update project type
- `DELETE /api/v1/project-types/{project_type_id}` - Delete project type

### Weather Data
- `GET /api/v1/weather/` - List weather data
- `GET /api/v1/weather/{weather_id}` - Get weather data
- `GET /api/v1/weather/location/{location}/date/{date}` - Get weather by location and date
- `POST /api/v1/weather/` - Create weather data
- `PUT /api/v1/weather/{weather_id}` - Update weather data
- `DELETE /api/v1/weather/{weather_id}` - Delete weather data

## Query Parameters

Most list endpoints support:
- `skip` - Number of records to skip (pagination)
- `limit` - Number of records to return (pagination)
- Model-specific filters (e.g., `status`, `type`, `location`)

## Response Format

All responses follow a consistent format:
- **Single item**: Direct object
- **List**: `{items: [...], total: number, page: number, size: number}`
- **Error**: `{detail: "error message"}`

## Development

The backend is structured as follows:
```
backend/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── database.py        # Database configuration
│   └── __init__.py
├── api/
│   └── v1/
│       ├── api.py         # Main API router
│       └── endpoints/      # Individual endpoint modules
├── schemas/               # Pydantic schemas
├── core/                  # Core configuration
└── requirements.txt       # Dependencies
```
