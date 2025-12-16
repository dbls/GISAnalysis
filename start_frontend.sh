#!/bin/bash

# Start script for GIS Analysis Frontend

echo "======================================"
echo "Starting GIS Analysis Frontend"
echo "======================================"
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    npm install
    echo ""
fi

echo "Starting React development server"
echo "Frontend will open at http://localhost:3000"
echo ""
echo "Make sure the backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start
