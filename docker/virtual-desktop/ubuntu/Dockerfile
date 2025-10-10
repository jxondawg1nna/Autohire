# Ubuntu Desktop Container for Virtual Desktop Environment
FROM ubuntu:22.04

LABEL maintainer="Autohire Visual Operator Team"
LABEL description="Ubuntu Desktop Environment for Virtual Desktop Operations"

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set VNC configuration
ENV VNC_RESOLUTION=1920x1080
ENV VNC_COL_DEPTH=24
ENV VNC_PORT=5901
ENV NOVNC_PORT=6080
ENV DISPLAY=:1

# Install system packages
RUN apt-get update && apt-get install -y \
    # Desktop environment
    ubuntu-desktop-minimal \
    xfce4 \
    xfce4-goodies \
    \
    # VNC server and web client
    tigervnc-standalone-server \
    tigervnc-xorg-extension \
    novnc \
    websockify \
    \
    # Web browsers
    firefox \
    wget \
    curl \
    \
    # Development tools
    git \
    python3 \
    python3-pip \
    nodejs \
    npm \
    code-server \
    \
    # System utilities
    htop \
    neofetch \
    nano \
    vim \
    unzip \
    zip \
    \
    # Graphics and media
    imagemagick \
    ffmpeg \
    pulseaudio \
    alsa-utils \
    \
    # Network tools
    net-tools \
    iputils-ping \
    openssh-client \
    \
    # Fonts
    fonts-liberation \
    fonts-dejavu-core \
    \
    # Additional utilities
    dbus-x11 \
    x11-utils \
    x11-apps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Visual Studio Code
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg \
    && install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/ \
    && sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list' \
    && apt-get update \
    && apt-get install -y code \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create desktop user
RUN useradd -m -s /bin/bash desktop \
    && echo 'desktop:desktop' | chpasswd \
    && usermod -aG sudo desktop

# Set up VNC for desktop user
USER desktop
WORKDIR /home/desktop

# Create VNC directory and set password
RUN mkdir -p ~/.vnc \
    && echo 'desktop' | vncpasswd -f > ~/.vnc/passwd \
    && chmod 600 ~/.vnc/passwd

# Create VNC startup script
RUN echo '#!/bin/bash' > ~/.vnc/xstartup \
    && echo 'unset SESSION_MANAGER' >> ~/.vnc/xstartup \
    && echo 'unset DBUS_SESSION_BUS_ADDRESS' >> ~/.vnc/xstartup \
    && echo 'exec startxfce4' >> ~/.vnc/xstartup \
    && chmod +x ~/.vnc/xstartup

# Create desktop directories
RUN mkdir -p ~/Desktop ~/Documents ~/Downloads

# Switch back to root to create startup scripts
USER root

# Create startup script
COPY scripts/start-desktop.sh /usr/local/bin/start-desktop.sh
RUN chmod +x /usr/local/bin/start-desktop.sh

# Create noVNC configuration
RUN mkdir -p /opt/novnc \
    && git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify.git /opt/novnc/utils/websockify

# Create supervisor configuration for managing services
RUN apt-get update && apt-get install -y supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create logging directories
RUN mkdir -p /var/log/supervisor /var/log/vnc /var/log/novnc

# Expose ports
EXPOSE $VNC_PORT $NOVNC_PORT 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "Xtigervnc" && pgrep -f "websockify" || exit 1

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/start-desktop.sh"]

# Default command
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]