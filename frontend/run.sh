#!/bin/bash
# Script to run the Streamlit frontend application

echo "Starting ÉpítAI Construction Management Frontend..."
echo "Activating virtual environment..."

# Activate virtual environment
source venv/bin/activate

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    echo "🐍 Python version: $(python --version)"
    echo ""
    echo "🚀 Starting Streamlit application..."
    echo "📱 The app will be available at: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop the application"
    echo ""
    
    # Run Streamlit
    streamlit run app.py
else
    echo "❌ Failed to activate virtual environment"
    echo "Please run: source venv/bin/activate"
    exit 1
fi
