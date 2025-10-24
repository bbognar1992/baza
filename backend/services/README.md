# Services Directory

The `services` directory contains the business logic layer of the FastAPI backend. These services handle complex operations, data processing, and integration with external systems.

## 📁 Directory Structure

```
services/
├── __init__.py                 # Services package
├── base.py                     # Base service class with common CRUD operations
├── project_service.py          # Project management business logic
├── resource_service.py         # Resource management business logic
├── material_service.py         # Material management business logic
├── scheduling_service.py       # Scheduling and timeline management
├── analytics_service.py        # Reporting and analytics
├── notification_service.py     # Alerts and notifications
├── weather_service.py          # Weather data management
└── README.md                   # This documentation
```

## 🏗️ Service Architecture

### Base Service (`base.py`)
- **Purpose**: Provides common CRUD operations for all services
- **Features**: 
  - Generic create, read, update, delete operations
  - Pagination support
  - Filtering capabilities
  - Error handling with database rollback
  - Logging integration

### Project Service (`project_service.py`)
- **Purpose**: Handles project-related business logic
- **Key Features**:
  - Create projects with locations and members
  - Calculate project costs (materials + labor)
  - Update project progress and status
  - Get project timeline with phases and tasks
  - Find overdue projects
  - Project performance metrics

### Resource Service (`resource_service.py`)
- **Purpose**: Manages human resources and assignments
- **Key Features**:
  - Resource availability management
  - Workload calculation and utilization metrics
  - Resource assignment to projects
  - Earnings calculation
  - Search and filtering capabilities

### Material Service (`material_service.py`)
- **Purpose**: Handles material inventory and procurement
- **Key Features**:
  - Stock level management
  - Low stock alerts
  - Material cost calculations
  - Supplier management
  - Material ordering workflow

### Scheduling Service (`scheduling_service.py`)
- **Purpose**: Manages project scheduling and timeline optimization
- **Key Features**:
  - Create project schedules
  - Resource schedule management
  - Weather impact analysis
  - Resource allocation optimization
  - Critical path analysis

### Analytics Service (`analytics_service.py`)
- **Purpose**: Provides reporting and analytics capabilities
- **Key Features**:
  - Project analytics and KPIs
  - Resource utilization metrics
  - Financial analytics
  - Productivity metrics
  - Dashboard summary data

### Notification Service (`notification_service.py`)
- **Purpose**: Manages alerts and notifications
- **Key Features**:
  - Overdue project alerts
  - Low stock notifications
  - Task deadline reminders
  - Resource availability alerts
  - Email/SMS notification support

### Weather Service (`weather_service.py`)
- **Purpose**: Handles weather data and forecasting
- **Key Features**:
  - Weather forecast retrieval
  - Work suitability analysis
  - Weather alerts and warnings
  - Schedule recommendations
  - Weather statistics

## 🔧 Usage Examples

### Project Service
```python
from services.project_service import ProjectService

# Initialize service
project_service = ProjectService(db)

# Create project with details
project = project_service.create_project_with_details(
    project_data={
        'project_name': 'New Building',
        'client_name': 'ABC Corp',
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=90)
    },
    locations=[{'location_name': 'Site A', 'address': '123 Main St'}],
    members=[{'resource_id': 1, 'role_in_project': 'Site Manager'}]
)

# Calculate project costs
costs = project_service.calculate_project_costs(project.project_id)
```

### Resource Service
```python
from services.resource_service import ResourceService

# Initialize service
resource_service = ResourceService(db)

# Get resource workload
workload = resource_service.get_resource_workload(
    resource_id=1,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=30)
)

# Get available resources
available = resource_service.get_available_resources('Alkalmazott')
```

### Analytics Service
```python
from services.analytics_service import AnalyticsService

# Initialize service
analytics = AnalyticsService(db)

# Get project analytics
project_analytics = analytics.get_project_analytics()

# Get dashboard summary
dashboard = analytics.get_dashboard_summary()
```

## 🎯 Service Benefits

### 1. **Separation of Concerns**
- Business logic separated from API endpoints
- Easier testing and maintenance
- Reusable across different API versions

### 2. **Complex Operations**
- Handle multi-table operations
- Transaction management
- Data validation and business rules

### 3. **Performance Optimization**
- Efficient database queries
- Caching strategies
- Bulk operations

### 4. **Error Handling**
- Consistent error management
- Database rollback on failures
- Detailed logging

### 5. **Extensibility**
- Easy to add new business logic
- Service composition
- Plugin architecture support

## 🔄 Service Integration

Services are designed to work together:

```python
# Example: Complete project setup
def setup_new_project(project_data, locations, members, materials):
    # Create project
    project_service = ProjectService(db)
    project = project_service.create_project_with_details(
        project_data, locations, members
    )
    
    # Add materials
    material_service = MaterialService(db)
    for material_data in materials:
        material_service.create_material_order(
            material_data['material_id'],
            material_data['quantity'],
            project.project_id
        )
    
    # Create schedule
    scheduling_service = SchedulingService(db)
    schedule = scheduling_service.create_project_schedule(
        project.project_id,
        project.start_date
    )
    
    # Send notifications
    notification_service = NotificationService(db)
    notifications = notification_service.get_all_notifications()
    
    return project, schedule, notifications
```

## 📊 Service Metrics

Each service can provide metrics for monitoring:

- **Database query performance**
- **Business logic execution time**
- **Error rates and types**
- **Resource utilization**
- **Cache hit rates**

## 🚀 Future Enhancements

### Planned Features:
- **Caching Layer**: Redis integration for performance
- **Background Tasks**: Celery integration for async operations
- **External Integrations**: Weather APIs, email services
- **Machine Learning**: Predictive analytics and recommendations
- **Real-time Updates**: WebSocket support for live notifications

### Service Extensions:
- **Audit Service**: Track all changes and modifications
- **Integration Service**: Connect with external systems
- **Workflow Service**: Manage business process automation
- **Security Service**: Handle authentication and authorization
- **File Service**: Manage document and file operations

## 🧪 Testing Services

Services should be tested with:
- **Unit Tests**: Individual service methods
- **Integration Tests**: Service interactions
- **Performance Tests**: Load and stress testing
- **Mock Tests**: External service dependencies

## 📝 Best Practices

1. **Single Responsibility**: Each service handles one domain
2. **Dependency Injection**: Use database sessions as dependencies
3. **Error Handling**: Always handle exceptions gracefully
4. **Logging**: Log important operations and errors
5. **Documentation**: Document complex business logic
6. **Testing**: Write comprehensive tests for all services
7. **Performance**: Optimize database queries and operations
8. **Security**: Validate inputs and handle sensitive data properly
