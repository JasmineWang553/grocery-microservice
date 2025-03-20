#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e  

echo "Starting FastAPI app..."

if [ "$DEBUG" = "True" ]; then
    echo "Running in debug mode with debugpy attached"
    python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
