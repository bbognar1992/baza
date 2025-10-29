# Pontum Construction Management - Frontend

Streamlit-based frontend application for the Pontum Construction Management System.

## 🏗️ Project Structure

```
frontend/
├── venv/                    # Virtual environment
├── app.py                   # Main Streamlit application
├── components/              # Reusable UI components
│   ├── sidebar.py
│   └── project_details_tabs/
│       ├── basic_info.py
│       ├── locations.py
│       ├── material_costs.py
│       ├── phases.py
│       ├── schedule.py
│       └── team.py
├── pages/                   # Application pages
│   ├── home.py
│   ├── projects.py
│   ├── resources.py
│   ├── materials.py
│   ├── scheduling.py
│   └── ...
├── database.py             # Database configuration
├── default_data.py         # Sample data
├── requirements.txt        # Python dependencies
├── activate.sh            # Virtual environment activation script
├── run.sh                 # Application startup script
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# Option 1: Use the activation script
./activate.sh

# Option 2: Manual activation
source venv/bin/activate
```

### 2. Run the Application
```bash
# Option 1: Use the run script
./run.sh

# Option 2: Manual run
streamlit run app.py
```

### 3. Access the Application
- **URL**: http://localhost:8501
- **Port**: 8501 (default Streamlit port)

## 📦 Dependencies

The application uses the following key dependencies:

- **Streamlit**: Web application framework
- **SQLAlchemy**: Database ORM
- **Pandas**: Data manipulation
- **Plotly**: Interactive charts
- **Requests**: HTTP client
- **Google API Client**: Google services integration

## 🔧 Development

### Virtual Environment Management

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate
```

### Database Configuration

The application connects to the same database as the backend. Make sure the database is running and accessible.

### Environment Variables

Create a `.env` file in the frontend directory with:

```env
DATABASE_URL=postgresql://username:password@host:port/database
SQLALCHEMY_ECHO=False
```

## 📱 Features

### 🏠 **Dashboard**
- Project overview
- Resource utilization
- Material inventory status
- Recent activity

### 📋 **Project Management**
- Create and edit projects
- Project timeline and phases
- Team member assignment
- Progress tracking

### 👥 **Resource Management**
- Employee and contractor management
- Skill tracking
- Availability scheduling
- Workload distribution

### 📦 **Material Management**
- Inventory tracking
- Supplier management
- Cost analysis
- Reorder alerts

### 📅 **Scheduling**
- Project timeline planning
- Resource allocation
- Weather impact analysis
- Task dependencies

### 📊 **Analytics**
- Project performance metrics
- Resource utilization reports
- Cost analysis
- Progress tracking

## 🎨 UI Components

### Sidebar Navigation
- Home
- Projects
- Resources
- Materials
- Scheduling
- Analytics

### Project Details Tabs
- **Basic Info**: Project details and status
- **Locations**: Project sites and addresses
- **Team**: Team members and roles
- **Phases**: Project phases and timeline
- **Materials**: Material requirements and costs
- **Schedule**: Timeline and task management

## 🔄 Integration

### Backend API Integration
The frontend can integrate with the FastAPI backend for:
- Real-time data updates
- Advanced analytics
- External service integration
- Scalable architecture

### Database Integration
- Direct database access for real-time data
- SQLAlchemy ORM for data manipulation
- Alembic for database migrations

## 🚀 Deployment

### Local Development
```bash
./run.sh
```

### Production Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run with specific host and port
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Deployment
```bash
# Build Docker image
docker build -t epitai-frontend .

# Run Docker container
docker run -p 8501:8501 epitai-frontend
```

## 🛠️ Troubleshooting

### Common Issues

1. **Virtual Environment Not Found**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Connection Error**
   - Check database URL in `.env` file
   - Ensure database server is running
   - Verify network connectivity

3. **Port Already in Use**
   ```bash
   streamlit run app.py --server.port 8502
   ```

4. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Logs and Debugging

- Streamlit logs are displayed in the terminal
- Use `st.write()` for debugging in the app
- Check browser console for frontend errors

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)

## 🤝 Contributing

1. Activate virtual environment
2. Make your changes
3. Test the application
4. Update requirements.txt if needed
5. Commit your changes

## 📄 License

This project is part of the Pontum Construction Management System.
