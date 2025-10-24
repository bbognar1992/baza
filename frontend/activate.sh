#!/bin/bash
# Script to activate the frontend virtual environment

echo "Activating frontend virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "To run the Streamlit app:"
echo "  streamlit run app.py"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
