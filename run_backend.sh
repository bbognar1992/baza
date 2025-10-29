#!/bin/bash

# Pontum Construction Management System - Backend Run Script
# This script provides various options to run the backend API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Pontum Backend Management${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from env.example..."
        if [ -f "backend/env.example" ]; then
            cp backend/env.example .env
            print_status "Created .env file from template. Please update with your database credentials."
        else
            print_error "No env.example file found. Please create a .env file manually."
            exit 1
        fi
    fi
}

# Function to run backend with Docker
run_docker() {
    print_status "Starting backend with Docker..."
    cd backend
    docker build -t baza-backend .
    docker run -d \
        --name baza-backend \
        -p 8000:8000 \
        --env-file ../.env \
        baza-backend
    print_status "Backend started on http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
}

# Function to run backend with Docker Compose
run_compose() {
    print_status "Starting backend with Docker Compose..."
    docker-compose up -d backend
    print_status "Backend started on http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
}

# Function to run backend locally (development)
run_local() {
    print_status "Starting backend locally (development mode)..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    
    # Run the application
    print_status "Starting FastAPI server..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to stop backend
stop_backend() {
    print_status "Stopping backend..."
    
    # Stop Docker container if running
    if docker ps -q -f name=baza-backend | grep -q .; then
        docker stop baza-backend
        docker rm baza-backend
        print_status "Docker container stopped and removed."
    fi
    
    # Stop Docker Compose services
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        print_status "Docker Compose services stopped."
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing backend logs..."
    if docker ps -q -f name=baza-backend | grep -q .; then
        docker logs -f baza-backend
    else
        print_error "Backend container is not running."
    fi
}

# Function to show status
show_status() {
    print_status "Backend Status:"
    echo ""
    
    # Check Docker container
    if docker ps -q -f name=baza-backend | grep -q .; then
        print_status "✅ Docker container is running"
        echo "   Container: baza-backend"
        echo "   Port: 8000"
        echo "   URL: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
    else
        print_warning "❌ Docker container is not running"
    fi
    
    # Check if port is in use
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_status "✅ Port 8000 is in use"
    else
        print_warning "❌ Port 8000 is not in use"
    fi
}

# Function to test API
test_api() {
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "✅ Health check passed"
    else
        print_error "❌ Health check failed"
        return 1
    fi
    
    # Test root endpoint
    if curl -s http://localhost:8000/ > /dev/null; then
        print_status "✅ Root endpoint accessible"
    else
        print_error "❌ Root endpoint not accessible"
        return 1
    fi
    
    print_status "✅ API is working correctly"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  docker     Run backend with Docker"
    echo "  compose    Run backend with Docker Compose"
    echo "  local      Run backend locally (development)"
    echo "  stop       Stop backend services"
    echo "  logs       Show backend logs"
    echo "  status     Show backend status"
    echo "  test       Test API endpoints"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 docker     # Start with Docker"
    echo "  $0 local      # Start locally for development"
    echo "  $0 status     # Check if backend is running"
    echo "  $0 test       # Test API endpoints"
}

# Main script logic
main() {
    print_header
    
    # Check prerequisites
    check_docker
    check_env
    
    case "${1:-help}" in
        "docker")
            run_docker
            ;;
        "compose")
            run_compose
            ;;
        "local")
            run_local
            ;;
        "stop")
            stop_backend
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "test")
            test_api
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"

