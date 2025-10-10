#!/bin/bash
set -e

echo "Starting Autohire Virtual Desktop Environment..."

# Set default values if not provided
VNC_RESOLUTION=${VNC_RESOLUTION:-1920x1080}
VNC_COL_DEPTH=${VNC_COL_DEPTH:-24}
VNC_PORT=${VNC_PORT:-5901}
NOVNC_PORT=${NOVNC_PORT:-6080}
DISPLAY=${DISPLAY:-:1}

# Create necessary directories
mkdir -p /tmp/.X11-unix /var/run/dbus

# Fix permissions
chown desktop:desktop /home/desktop -R
chmod 755 /tmp/.X11-unix

# Start D-Bus
echo "Starting D-Bus service..."
service dbus start

# Start PulseAudio for audio support
echo "Starting PulseAudio..."
su - desktop -c "pulseaudio --start --log-target=syslog" || true

# Kill any existing VNC sessions
echo "Cleaning up existing VNC sessions..."
su - desktop -c "vncserver -kill $DISPLAY" 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start VNC server
echo "Starting VNC server on display $DISPLAY..."
su - desktop -c "vncserver $DISPLAY -geometry $VNC_RESOLUTION -depth $VNC_COL_DEPTH -localhost no"

# Wait for VNC server to start
echo "Waiting for VNC server to initialize..."
timeout=30
while [ $timeout -gt 0 ]; do
    if su - desktop -c "vncserver -list" | grep -q "$DISPLAY"; then
        echo "VNC server is running on display $DISPLAY"
        break
    fi
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "ERROR: VNC server failed to start within 30 seconds"
    exit 1
fi

# Start noVNC web client
echo "Starting noVNC web client on port $NOVNC_PORT..."
cd /opt/novnc
./utils/novnc_proxy --vnc localhost:$VNC_PORT --listen $NOVNC_PORT &
NOVNC_PID=$!

# Wait for noVNC to start
echo "Waiting for noVNC to initialize..."
timeout=15
while [ $timeout -gt 0 ]; do
    if netstat -ln | grep -q ":$NOVNC_PORT"; then
        echo "noVNC is running on port $NOVNC_PORT"
        break
    fi
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "WARNING: noVNC failed to start within 15 seconds"
fi

# Create desktop environment customization
echo "Configuring desktop environment..."
su - desktop -c "
# Create desktop shortcuts
cat > ~/Desktop/Terminal.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Terminal
Comment=Open Terminal
Exec=xfce4-terminal
Icon=utilities-terminal
Path=
Terminal=false
StartupNotify=true
EOF

cat > ~/Desktop/Firefox.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Firefox
Comment=Web Browser
Exec=firefox
Icon=firefox
Path=
Terminal=false
StartupNotify=true
EOF

cat > ~/Desktop/Chrome.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Google Chrome
Comment=Web Browser
Exec=google-chrome-stable
Icon=google-chrome
Path=
Terminal=false
StartupNotify=true
EOF

cat > ~/Desktop/VSCode.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Visual Studio Code
Comment=Code Editor
Exec=code
Icon=code
Path=
Terminal=false
StartupNotify=true
EOF

# Make desktop files executable
chmod +x ~/Desktop/*.desktop

# Set XFCE panel configuration
mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml/
"

echo "Virtual Desktop Environment started successfully!"
echo "VNC Server: localhost:$VNC_PORT"
echo "noVNC Web Client: http://localhost:$NOVNC_PORT"
echo "Display: $DISPLAY"

# Function to handle shutdown
cleanup() {
    echo "Shutting down Virtual Desktop Environment..."
    
    # Kill noVNC
    if [ ! -z "$NOVNC_PID" ]; then
        kill $NOVNC_PID 2>/dev/null || true
    fi
    
    # Kill VNC server
    su - desktop -c "vncserver -kill $DISPLAY" 2>/dev/null || true
    
    # Stop PulseAudio
    su - desktop -c "pulseaudio --kill" 2>/dev/null || true
    
    echo "Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT SIGQUIT

# Keep the script running and monitor services
echo "Monitoring services..."
while true; do
    # Check if VNC server is still running
    if ! su - desktop -c "vncserver -list" | grep -q "$DISPLAY"; then
        echo "ERROR: VNC server has stopped unexpectedly"
        exit 1
    fi
    
    # Check if noVNC is still running
    if ! netstat -ln | grep -q ":$NOVNC_PORT"; then
        echo "WARNING: noVNC has stopped, attempting to restart..."
        cd /opt/novnc
        ./utils/novnc_proxy --vnc localhost:$VNC_PORT --listen $NOVNC_PORT &
        NOVNC_PID=$!
    fi
    
    sleep 10
done