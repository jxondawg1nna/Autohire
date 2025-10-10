#!/bin/bash
# Startup script for Visual Desktop Operator

set -e

echo "Starting Visual Desktop Operator..."

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to cleanup on exit
cleanup() {
    log "Shutting down..."
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null || true
    fi
    if [ ! -z "$VNC_PID" ]; then
        kill $VNC_PID 2>/dev/null || true
    fi
    if [ ! -z "$FLUXBOX_PID" ]; then
        kill $FLUXBOX_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Set display variables
export DISPLAY=:99
export SCREEN_WIDTH=${SCREEN_WIDTH:-1920}
export SCREEN_HEIGHT=${SCREEN_HEIGHT:-1080}
export SCREEN_DEPTH=${SCREEN_DEPTH:-24}

log "Setting up virtual display (${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH})"

# Start Xvfb (X Virtual Framebuffer)
Xvfb :99 -screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} -ac -nolisten tcp -dpi 96 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Verify Xvfb is running
if ! kill -0 $XVFB_PID 2>/dev/null; then
    log "ERROR: Failed to start Xvfb"
    exit 1
fi

log "Xvfb started successfully (PID: $XVFB_PID)"

# Start Fluxbox window manager
fluxbox &
FLUXBOX_PID=$!
sleep 2

log "Fluxbox window manager started (PID: $FLUXBOX_PID)"

# Start VNC server for remote access (if enabled)
if [ "${ENABLE_VNC:-false}" = "true" ]; then
    log "Starting VNC server on port 5900"
    x11vnc -display :99 -forever -usepw -create -rfbport 5900 &
    VNC_PID=$!
    log "VNC server started (PID: $VNC_PID)"
fi

# Wait a moment for everything to stabilize
sleep 3

# Set up Python path
export PYTHONPATH=/app:$PYTHONPATH

# Change to application directory
cd /app

# Initialize logging directory
mkdir -p /app/logs

# Run database migrations if needed
log "Checking database migrations..."
python3 -c "
import sys
sys.path.append('/app')
try:
    from app.core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    # In production, you might want to exit here
" || log "Warning: Database check failed"

# Download YOLO models if not present
log "Checking AI models..."
python3 -c "
import os
from pathlib import Path

models_dir = Path('/app/models')
models_dir.mkdir(exist_ok=True)

# Check for YOLO model
yolo_model_path = models_dir / 'yolov8n.pt'
if not yolo_model_path.exists():
    print('Downloading YOLOv8 model...')
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # This will download the model
        print('YOLO model downloaded successfully')
    except Exception as e:
        print(f'Warning: Could not download YOLO model: {e}')
else:
    print('YOLO model already present')
" || log "Warning: AI model setup failed"

# Set environment variables for the application
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export ENVIRONMENT=${ENVIRONMENT:-production}
export ENABLE_PERFORMANCE_MONITORING=${ENABLE_PERFORMANCE_MONITORING:-true}
export MAX_CONCURRENT_SESSIONS=${MAX_CONCURRENT_SESSIONS:-5}

# Security settings
export SAFETY_ENABLED=${SAFETY_ENABLED:-true}
export DRY_RUN_MODE=${DRY_RUN_MODE:-false}
export REQUIRE_CONFIRMATION=${REQUIRE_CONFIRMATION:-false}

log "Environment configuration:"
log "  - Display: $DISPLAY (${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH})"
log "  - Log Level: $LOG_LEVEL"
log "  - Environment: $ENVIRONMENT"
log "  - Safety Enabled: $SAFETY_ENABLED"
log "  - Max Concurrent Sessions: $MAX_CONCURRENT_SESSIONS"

# Start the Visual Desktop Operator application
log "Starting Visual Desktop Operator application..."

if [ "${DEVELOPMENT_MODE:-false}" = "true" ]; then
    log "Running in development mode with hot reload"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
else
    log "Running in production mode"
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
fi

# This should not be reached, but just in case
log "Application exited unexpectedly"
cleanup