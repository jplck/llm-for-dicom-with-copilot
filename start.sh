#!/bin/bash

# DICOM Viewer Application Startup Script

echo "🏥 Starting DICOM Image Viewer..."
echo "=================================="

# Check if we're in a dev container
if [ -f /.dockerenv ]; then
    echo "✓ Running in dev container"
else
    echo "⚠️  Not in dev container - installing dependencies..."
    pip install -r requirements.txt
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

echo "🚀 Starting Flask development server..."
echo "📝 Access the application at: http://localhost:5000"
echo "🔍 Upload DICOM files to view them in the gallery"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python app.py