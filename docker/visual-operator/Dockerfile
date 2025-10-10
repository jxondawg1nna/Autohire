# Visual Desktop Operator Docker Configuration
# Specialized container for desktop automation with GUI access

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for desktop automation
RUN apt-get update && apt-get install -y \
    # Python and basic tools
    python3.10 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    # GUI and display dependencies
    xvfb \
    x11vnc \
    fluxbox \
    xterm \
    # Desktop automation dependencies
    libxtst6 \
    libxss1 \
    libgconf-2-4 \
    libnss3 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Input simulation dependencies
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    # Additional utilities
    wget \
    curl \
    unzip \
    git \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install additional dependencies for Visual Desktop Operator
RUN pip3 install --no-cache-dir \
    python-json-logger==2.0.7 \
    structlog==23.2.0 \
    # Add any specific versions needed
    && pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Create necessary directories
RUN mkdir -p /app/logs /app/storage /app/models /app/screenshots /app/backups

# Copy application code
COPY backend/app /app/app
COPY backend/main.py /app/main.py

# Copy startup scripts
COPY docker/visual-operator/scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Create user for running the application (security best practice)
RUN useradd -m -s /bin/bash operator && \
    chown -R operator:operator /app && \
    # Add operator to necessary groups for GUI access
    usermod -a -G audio,video,input operator

# Switch to operator user
USER operator

# Set up virtual display
ENV DISPLAY=:99
ENV SCREEN_WIDTH=1920
ENV SCREEN_HEIGHT=1080
ENV SCREEN_DEPTH=24

# Expose ports
EXPOSE 8000 5900 6080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["/app/scripts/start.sh"]