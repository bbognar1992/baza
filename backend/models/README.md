# ÉpítAI Construction Management System - SQLAlchemy Models

This directory contains SQLAlchemy models for the ÉpítAI Construction Management System database.

## 📁 File Structure

```
models/
├── __init__.py              # Model imports and exports
├── base.py                  # Base configuration and utilities
├── user.py                  # User model
├── profession_type.py       # Profession type model
├── resource.py              # Resource model
├── project_type.py          # Project type model
├── project.py               # Project, ProjectLocation, ProjectMember models
├── phase.py                 # Phase model
├── task.py                  # Task model
├── project_phase.py         # ProjectPhase model
├── project_task.py          # ProjectTask model
├── task_assignment.py       # TaskAssignment model
├── material.py              # Material, ProjectMaterial models
├── weather_data.py          # WeatherData model
└── README.md                # This file
```

## 🗄️ Database Models

### Core Entities
- **User** - System users and employees
- **ProfessionType** - Job categories and skill levels
- **Resource** - Human resources (employees, subcontractors, suppliers)
- **ProjectType** - Types of construction projects

### Project Management
- **Project** - Individual construction projects
- **ProjectLocation** - Project locations (many-to-many)
- **ProjectMember** - Project team members (many-to-many)
- **Phase** - Project phases with their characteristics
- **Task** - Individual tasks within phases
- **ProjectPhase** - Project-specific phase instances
- **ProjectTask** - Project-specific task instances

### Resource Management
- **TaskAssignment** - Resource assignments to specific tasks
- **Material** - Construction materials and supplies
- **ProjectMaterial** - Project material requirements (many-to-many)

### Scheduling
- **WeatherData** - Weather information for scheduling decisions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

### 2. Set Environment Variables

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/epitai_db"
# or for SQLite testing:
export DATABASE_URL="sqlite:///epitai.db"
```

### 3. Initialize Database

```python
from database import initialize_database

# Initialize database with sample data
initialize_database()
```

### 4. Use Models

```python
from database import get_db_session
from models import Project, User, Resource

# Create a new project
with get_db_session() as session:
    project = Project(
        project_name="My Construction Project",
        client_name="Client Name",
        status="Tervezés alatt",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31)
    )
    session.add(project)
    session.commit()
```

## 📊 Model Features

### Common Features
- **Timestamps** - Automatic `created_at` and `updated_at` fields
- **Validation** - Database-level constraints and checks
- **Relationships** - Proper foreign key relationships
- **Serialization** - `to_dict()` methods for JSON conversion
- **Properties** - Computed properties for common operations

### Special Features
- **Weather-based scheduling** - Weather data integration
- **Progress tracking** - Multi-level progress tracking
- **Resource management** - Employee, subcontractor, and supplier management
- **Material inventory** - Stock management and reorder levels
- **Cost tracking** - Labor and material cost calculations

## 🔧 Usage Examples

### Creating a Project

```python
from database import get_db_session
from models import Project, ProjectType, User

with get_db_session() as session:
    # Get project type and manager
    project_type = session.query(ProjectType).filter_by(name="Földszintes ház").first()
    manager = session.query(User).filter_by(email="manager@company.com").first()
    
    # Create project
    project = Project(
        project_name="New House Project",
        client_name="John Doe",
        project_type_id=project_type.project_type_id,
        project_manager_id=manager.user_id,
        status="Tervezés alatt",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        budget=250000.00,
        priority="Magas"
    )
    session.add(project)
    session.commit()
```

### Querying with Relationships

```python
from database import get_db_session
from models import Project

with get_db_session() as session:
    # Get projects with all relationships
    projects = session.query(Project).options(
        joinedload(Project.project_type),
        joinedload(Project.project_manager),
        joinedload(Project.members).joinedload(ProjectMember.resource),
        joinedload(Project.locations)
    ).all()
    
    for project in projects:
        print(f"Project: {project.project_name}")
        print(f"Type: {project.project_type.name}")
        print(f"Manager: {project.project_manager.full_name}")
        print(f"Team size: {project.team_size}")
        print(f"Locations: {len(project.locations)}")
```

### Material Management

```python
from database import get_db_session
from models import Material, ProjectMaterial

with get_db_session() as session:
    # Check low stock materials
    low_stock_materials = session.query(Material).filter(
        Material.current_stock <= Material.reorder_level
    ).all()
    
    for material in low_stock_materials:
        print(f"Low stock: {material.name} ({material.current_stock} remaining)")
        print(f"Needs reorder: {material.needs_reorder}")
```

### Weather-based Scheduling

```python
from database import get_db_session
from models import WeatherData

with get_db_session() as session:
    # Get weather data for scheduling
    weather = session.query(WeatherData).filter_by(
        location="Győr",
        date=date.today()
    ).first()
    
    if weather:
        print(f"Weather: {weather.weather_summary}")
        print(f"Can work outdoor: {weather.is_suitable_for_outdoor_work}")
        print(f"Recommendation: {weather.work_recommendation}")
```

## 🛠️ Database Operations

### Initialize Database

```python
from database import initialize_database

# Initialize with sample data
initialize_database()
```

### Reset Database

```python
from database import reset_database

# Drop and recreate all tables
reset_database()
```

### Check Connection

```python
from database import check_database_connection, get_database_info

# Check if database is accessible
if check_database_connection():
    info = get_database_info()
    print(f"Database: {info['type']} {info['version']}")
```

## 📋 Model Relationships

```
User (1) ──→ (N) Project (project_manager)
Project (1) ──→ (N) ProjectMember (N) ──→ (1) Resource
Project (1) ──→ (N) ProjectLocation
Project (1) ──→ (N) ProjectPhase (1) ──→ (1) Phase
ProjectPhase (1) ──→ (N) ProjectTask (1) ──→ (1) Task
ProjectTask (1) ──→ (N) TaskAssignment (N) ──→ (1) Resource
Project (1) ──→ (N) ProjectMaterial (N) ──→ (1) Material
Resource (1) ──→ (N) Material (supplier)
Task (1) ──→ (1) ProfessionType
Phase (1) ──→ (1) ProjectType
```

## 🔍 Query Examples

### Get Active Projects with Progress

```python
active_projects = session.query(Project).filter(
    Project.status.in_(['Tervezés alatt', 'Folyamatban', 'Késésben'])
).all()
```

### Get Resources by Type

```python
employees = session.query(Resource).filter_by(type='Alkalmazott').all()
subcontractors = session.query(Resource).filter_by(type='Alvállalkozó').all()
suppliers = session.query(Resource).filter_by(type='Beszállító').all()
```

### Get Project Progress by Phase

```python
project_phases = session.query(ProjectPhase).filter_by(
    project_id=project_id
).all()

for phase in project_phases:
    print(f"{phase.phase.name}: {phase.progress_percent}%")
```

## 🚨 Error Handling

All models include proper error handling and validation:

- **Database constraints** - Prevent invalid data
- **Relationship integrity** - Foreign key constraints
- **Data validation** - Check constraints for enums
- **Transaction safety** - Automatic rollback on errors

## 📝 Notes

- Models use **SQLAlchemy 2.0** syntax
- All timestamps are **UTC** by default
- **Cascade deletes** are properly configured
- **Indexes** are optimized for common queries
- **Computed fields** are available as properties
- **JSON serialization** is supported via `to_dict()` methods
